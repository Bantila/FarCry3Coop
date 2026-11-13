"""Annotating x86 disassembler for FC3 binaries (capstone + PE import/string map).

Read-only. Resolves call targets, IAT slots, and string pushes so a function can be read
without a full decompiler.

Usage: python -I tools/fc3_dis.py <pe file> <start VA> [end VA | length] [max instrs]
"""
import struct
import sys

import capstone

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

sys.path.insert(0, r"D:/Projects/Co-op Anything/FarCry3Coop-bantila/scripts")
sys.path.insert(0, r"D:/Projects/Co-op Anything/FarCryCoop/tools")
from fc3_addrmap import PE  # noqa: E402
from fc3_iat_reverse import build_map  # noqa: E402


def cstr(d, off, limit=96):
    if off is None:
        return None
    raw = d[off:off + limit].split(b"\0", 1)[0]
    if not raw:
        return None
    if len(raw) % 2 == 0 and raw.count(b"\0") == len(raw) // 2 - 1:
        try:
            return raw.decode("utf-16le")
        except UnicodeDecodeError:
            pass
    return raw.decode("latin-1", "replace")


def main(path, start, stop, maxn):
    pe = PE(path)
    d = pe.d
    _, iat = build_map(path)
    md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
    md.detail = True
    off = pe.va2off(start)
    if off is None:
        print("start VA not mapped")
        return
    code = d[off:off + max(4, stop - start)]
    n = 0
    for ins in md.disasm(code, start):
        n += 1
        notes = []
        for op in ins.operands:
            if op.type == capstone.CS_OP_IMM:
                v = op.imm
                o = pe.va2off(v)
                if pe.in_text(v):
                    notes.append("func 0x%08x" % v)
                elif v in iat:
                    notes.append("IAT %s" % iat[v])
                elif o is not None:
                    s = cstr(d, o)
                    if s and len(s) > 1 and all(0x20 <= ord(c) < 0x7f for c in s[:min(8, len(s))]):
                        notes.append("str=%r" % s[:64])
            elif op.type == capstone.CS_OP_MEM:
                disp = op.mem.disp
                if disp and not op.mem.base and not op.mem.index:
                    if disp in iat:
                        notes.append("import %s" % iat[disp])
                    else:
                        s = cstr(d, pe.va2off(disp))
                        if s and len(s) > 1:
                            notes.append("data %s -> %r" % ("%08x" % disp, s[:64]))
                        else:
                            notes.append("data %s" % ("%08x" % disp))
        print("0x%08x  %-24s %s %s%s" % (
            ins.address, ins.bytes.hex(), ins.mnemonic, ins.op_str,
            ("   ; " + " | ".join(notes)) if notes else ""))
        if n >= maxn or ins.address >= stop:
            break


if __name__ == "__main__":
    a = sys.argv[1:]
    start = int(a[1], 16)
    stop = int(a[2], 16) if len(a) > 2 else start + 0x400
    maxn = int(a[3], 16) if len(a) > 3 else 900
    main(a[0], start, stop, maxn)
