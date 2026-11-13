"""fc3_switch_context.py -- disassemble around a reference site in a Far Cry 3 PE module.

Two modes:
  prologue (default): find the function that contains the address. First the MSVC padding
  heuristic (a run of >=4 0xCC bytes before the address), then a nearest-first search over known
  prologue bytes, accepting only a candidate whose linear disassembly executes exactly through
  the site. The padding run after the start gives the function end.
  raw: disassemble --before .. --after around the site, no function bounds. Use this for sites in
  the middle of a large function (the launch-argument parser is one) where the padding heuristic
  finds no boundary.

Function bounds and prologue guesses are heuristics, not a disassembler's word: a wrong start can
desync the linear sweep, so read the output around the site marker, not from the first line.

Usage:
  python scripts/fc3_switch_context.py <pe path> <addr> [addr ...]
      [--mode prologue|raw|both] [--lookback BYTES] [--max BYTES]
      [--before BYTES] [--after BYTES] [--no-disasm]

Read-only analysis. Nothing here is written to the game folder.
"""
import sys
import argparse

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.path.insert(0, r"D:/Projects/Co-op Anything/FarCry3Coop-bantila/scripts")
from fc3_reloc_xref import PE, cs_for  # noqa: E402

PAD_MIN = 4


def _size(text):
    """argparse type that accepts 600, 0x256c or 04444."""
    return int(text, 0)
# x86 function-start fingerprints seen in the Far Cry 3 modules (longest first).
PROLOGUES = [b"\x55\x8b\xec", b"\x55\x8b\xf1", b"\x55\x33\xc0", b"\x53\x56", b"\x53\x8b",
             b"\x55", b"\x6a\xff", b"\x53", b"\x33\xc0", b"\xe9"]


def pad_run_before(d, off):
    """Offset just after the nearest 0xCC padding run that ends at or before off, else None."""
    run = 0
    i = off - 1
    while i >= 0 and run < 0x400:
        if d[i] == 0xCC:
            run += 1
            i -= 1
        else:
            break
    return (i + 1) if run >= PAD_MIN else None


def pad_run_after(d, off):
    """First byte of the nearest 0xCC padding run at or after off, else None."""
    i = off
    run = 0
    while i < len(d) and run < 0x400:
        if d[i] == 0xCC:
            run += 1
            i += 1
        else:
            break
    return (i - run) if run >= PAD_MIN else None


def lands_on(pe, cs, start_off, target_va, limit):
    """True when the linear disassembly from start_off executes exactly through target_va."""
    if cs is None:
        return True
    sva = pe.off2va(start_off)
    if sva is None:
        return False
    for ins in cs.disasm(pe.d[start_off:start_off + limit], sva):
        if ins.address == target_va:
            return True
        if ins.address > target_va:
            return False
    return False


def find_start(pe, cs, off, va, lookback, limit):
    """Return (start_off, how) for the function containing va, or (None, None)."""
    start = pad_run_before(pe.d, off)
    if start is not None and lands_on(pe, cs, start, va, limit):
        return start, "padding-run"
    lo = max(0, off - lookback)
    for pro in PROLOGUES:
        i = off - 1
        while i >= lo:
            j = pe.d.rfind(pro, lo, i + 1)
            if j < 0:
                break
            i = j - 1
            sva = pe.off2va(j)
            if sva is None or sva >= va:
                continue
            if lands_on(pe, cs, j, va, min(limit, va - sva + 16)):
                return j, "prologue %s" % pro.hex()
    return None, None


def dump(pe, cs, start_off, end_off, va):
    sva = pe.off2va(start_off)
    print("   bytes: %s" % pe.d[start_off:start_off + 48].hex())
    if cs is None:
        return []
    calls = []
    for ins in cs.disasm(pe.d[start_off:end_off], sva):
        mark = "   <== site" if ins.address == va else ""
        print("   %08x  %-24s %s%s" % (ins.address, ins.bytes.hex(),
                                       ins.mnemonic + " " + ins.op_str, mark))
        if ins.mnemonic in ("call", "jmp") and ins.op_str.startswith("0x"):
            calls.append((ins.address, ins.mnemonic, ins.op_str))
    return calls


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("path")
    ap.add_argument("addr", nargs="+")
    ap.add_argument("--mode", choices=("prologue", "raw", "both"), default="prologue")
    ap.add_argument("--lookback", type=_size, default=0x2000, help="max bytes searched back")
    ap.add_argument("--max", type=_size, default=0x1200, help="max disassembled bytes per function")
    ap.add_argument("--before", type=_size, default=0x180, help="raw mode: bytes before the site")
    ap.add_argument("--after", type=_size, default=0x400, help="raw mode: bytes after the site")
    ap.add_argument("--no-disasm", action="store_true")
    args = ap.parse_args()

    pe = PE(args.path)
    print("== %s: imagebase=0x%x machine=0x%x %d relocs =="
          % (args.path, pe.base, pe.machine, len(pe.reloc_entries())))
    cs = None if args.no_disasm else cs_for(pe.machine)
    seen = {}

    for a in args.addr:
        va = int(a, 16) if isinstance(a, str) else int(a)
        off = pe.va2off(va)
        if off is None:
            print("0x%08x -> not mapped" % va)
            continue
        start, how = (None, None)
        if args.mode in ("prologue", "both"):
            start, how = find_start(pe, cs, off, va, args.lookback, args.max + 0x1000)
        if start is None:
            if args.mode == "prologue":
                print("0x%08x -> no function start found (lookback %d); use --mode raw" % (va, args.lookback))
                continue
            lo = max(0, off - args.before)
            hi = off + args.after
            print("\n== site 0x%08x  raw range 0x%08x .. 0x%08x =="
                  % (va, pe.off2va(lo), pe.off2va(hi)))
            calls = dump(pe, cs, lo, hi, va)
        else:
            sva = pe.off2va(start)
            end = pad_run_after(pe.d, start + 1)
            if end is None or end - start > args.max:
                end = start + args.max
            if sva in seen:
                print("0x%08x -> same function 0x%08x (already printed)" % (va, sva))
                continue
            seen[sva] = True
            print("\n== site 0x%08x  function 0x%08x .. 0x%08x (%d bytes, %s) =="
                  % (va, sva, pe.off2va(end), end - start, how))
            calls = dump(pe, cs, start, end, va)
        if calls:
            print("   branches: " + ", ".join("%s 0x%08x -> %s" % (m, f, t) for f, m, t in calls[:30]))


main()
