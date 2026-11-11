#!/usr/bin/env python3
"""
fc3_mode_cascade.py -- disassemble a launch-mode cascade and report the mode ids it stores.

Far Cry 3 1.06 does not treat "-coop" as a boolean flag: the launch parser compares the token with
the list of mode names, and each branch stores that mode's 32-bit id into the global that the
session code reads later. This tool reads one cascade function and reports, in address order:

  * every "mov dword ptr [global], imm32" store (the global VA plus the mode id written into it),
  * every data reference in the same block that resolves to a printable string (the mode name or
  option that branch matched),
  * the cmp/test instructions, so the branch order can be read next to the stores,
  * the annotated listing.

Known cascade functions (1.06, recorded in NOTES.md):
  FC3.dll        0x11a8c440  body start; "-coop" at 0x11a8c533 reads [0x1216aee4] = 0x43521e6f and
                             stores it into [ebp+8]; "-domination" -> [0x1216aeec] = 0xab4fc8e2,
                             "-firestorm" -> [0x1216aefc] = 0xf66ffb87
  FC3_d3d11.dll  0x11aa08d0  "-coop" reads [0x1218ffe4] = 0x43521e6f; "-dash" -> [0x12190004] = 0x2100ced7

Read-only: the PE is opened for reading only, nothing is written and no game file is modified.

Usage:
  python -I scripts/fc3_mode_cascade.py <pe> <start VA> [--end <VA> | --limit N] [--no-strings]
                                        [--json]
  <pe> is a path, or a bare module name resolved against the 1.06 bin directory
  (H:/FarCryCoop/TestFC3/bin/). Disassembly stops at the first "ret" when both --end and --limit
  are absent, so a cascade is read as one function body.
Output:
  text sections (stores, data refs, cmp/test, listing), or a JSON summary with --json.
Exit code: 0 on success, 1 when capstone is missing.
"""
import sys
import argparse
import struct

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

try:
    import capstone
except Exception:
    print("capstone missing: python -m pip install capstone")
    sys.exit(1)

sys.path.insert(0, r"D:/Projects/Co-op Anything/FarCry3Coop-bantila/scripts")
sys.path.insert(0, r"D:/Projects/Co-op Anything/FarCryCoop/tools")
from fc3_addrmap import PE  # noqa: E402
from fc3_iat_reverse import build_map  # noqa: E402

BIN_106 = "H:/FarCryCoop/TestFC3/bin/"


def resolve(path):
    """Accept a full path, or a bare module name resolved against the 1.06 bin directory."""
    if "/" in path or "\\" in path:
        return path
    return BIN_106 + path


def cstr(d, off, limit=96):
    """Printable NUL-terminated ASCII string at a file offset, else None."""
    if off is None:
        return None
    raw = d[off:off + limit].split(b"\0", 1)[0]
    if not raw or any(b < 0x20 or b > 0x7E for b in raw):
        return None
    return raw.decode("ascii", "replace")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pe", help="module path or bare module name in the 1.06 bin directory")
    ap.add_argument("start", help="cascade function start VA (hex)")
    ap.add_argument("--end", help="last VA to disassemble (hex)")
    ap.add_argument("--limit", type=int, default=0, help="max instructions")
    ap.add_argument("--no-strings", action="store_true", help="skip data-to-string resolution")
    ap.add_argument("--json", action="store_true", help="also print a machine-readable summary")
    a = ap.parse_args()

    path = resolve(a.pe)
    pe = PE(path)
    d = pe.d
    _, iat = build_map(path)
    md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
    md.detail = True

    start = int(a.start, 16)
    end = int(a.end, 16) if a.end else None
    off = pe.va2off(start)
    if off is None:
        print("%s: %#x is not mapped" % (path, start))
        return
    stop_off = pe.va2off(end) if end else pe.text[2] + pe.text[3] - 1
    code = d[off:stop_off + 1]

    # a ret stops the body only when the caller did not give an explicit range
    stop_at_ret = end is None and a.limit == 0
    stores, writes, reads, data_refs, branches, listing = [], [], [], [], [], []
    for ins in md.disasm(code, start):
        if end is not None and ins.address > end:
            break
        if a.limit and len(listing) >= a.limit:
            break
        notes = []
        for op in ins.operands:
            if op.type == capstone.CS_OP_IMM:
                v = op.imm
                if pe.in_text(v):
                    notes.append("func %#010x" % v)
                elif v in iat:
                    notes.append("IAT %s" % iat[v])
                else:
                    s = cstr(d, pe.va2off(v)) if not a.no_strings else None
                    if s and len(s) > 1:
                        notes.append("str=%r" % s[:64])
                        data_refs.append((ins.address, v, s[:64]))
            elif op.type == capstone.CS_OP_MEM:
                disp = op.mem.disp
                if disp and not op.mem.base and not op.mem.index:
                    if disp in iat:
                        notes.append("import %s" % iat[disp])
                    else:
                        s = cstr(d, pe.va2off(disp)) if not a.no_strings else None
                        if s and len(s) > 1:
                            notes.append("data %#010x -> %r" % (disp, s[:64]))
                            data_refs.append((ins.address, disp, s[:64]))
                        else:
                            off = pe.va2off(disp)
                            val = struct.unpack_from("<I", d, off)[0] if off is not None else None
                            reads.append((ins.address, ins.mnemonic, disp, val))
                            notes.append("data %#010x%s" % (disp, "" if val is None else " = %#010x" % val))
        if ins.mnemonic == "mov" and len(ins.operands) == 2:
            dst, src = ins.operands
            if (dst.type == capstone.CS_OP_MEM and not dst.mem.base and not dst.mem.index
                    and dst.mem.disp and src.type == capstone.CS_OP_IMM):
                stores.append((ins.address, dst.mem.disp, src.imm))
        if ins.mnemonic == "mov" and len(ins.operands) == 2 and ins.operands[0].type == capstone.CS_OP_MEM:
            writes.append((ins.address, ins.op_str.split(", ", 1)[1] if ", " in ins.op_str else "", ins.op_str))
        if ins.mnemonic in ("cmp", "test"):
            branches.append((ins.address, ins.mnemonic, ins.op_str))
        listing.append((ins.address, ins.bytes.hex(), ins.mnemonic, ins.op_str, notes))
        if ins.mnemonic == "ret" and stop_at_ret:
            break

    if not listing:
        print("%s: nothing disassembled at %#x" % (path, start))
        return

    print("=" * 70)
    print("%s base=%#x cascade %#x..%#x" % (path, pe.base, start, listing[-1][0]))
    print("instructions=%d stores=%d writes=%d reads=%d data_refs=%d cmp_test=%d"
          % (len(listing), len(stores), len(writes), len(reads), len(data_refs), len(branches)))
    print("-- stores (global <- mode id) --")
    for va, disp, imm in stores:
        print("  %#010x  [%.8s] = %#010x" % (va, "%08x" % disp, imm))
    print("-- writes (any memory destination <- source) --")
    for va, src, op in writes:
        print("  %#010x  %-34s src=%s" % (va, op, src))
    print("-- global reads (value held in the file at that global) --")
    for va, mnem, disp, val in reads:
        print("  %#010x  %-6s [%.8s]%s" % (va, mnem, "%08x" % disp,
                                           "" if val is None else " = %#010x" % val))
    print("-- data refs --")
    for va, sva, sval in data_refs:
        print("  %#010x  -> %#010x  %r" % (va, sva, sval))
    print("-- cmp/test --")
    for va, mnem, op in branches:
        print("  %#010x  %s %s" % (va, mnem, op))
    print("-- listing --")
    for va, bts, mnem, op, notes in listing:
        print("  %#010x  %-24s %s %s%s" % (
            va, bts, mnem, op, ("   ; " + " | ".join(notes)) if notes else ""))

    if a.json:
        import json
        print(json.dumps({
            "module": path,
            "start": start,
            "end": listing[-1][0],
            "stores": [{"va": s[0], "global": s[1], "value": s[2]} for s in stores],
            "writes": [{"va": s[0], "op": s[2]} for s in writes],
            "reads": [{"va": s[0], "mnemonic": s[1], "global": s[2], "static_value": s[3]} for s in reads],
            "data_refs": [{"va": r[0], "data_va": r[1], "text": r[2]} for r in data_refs],
        }, ensure_ascii=False))


if __name__ == "__main__":
    main()
