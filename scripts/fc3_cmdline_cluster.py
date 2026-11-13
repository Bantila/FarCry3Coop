"""Map a command-line switch-parsing cluster in a Far Cry 3 PE file.

Given a switch string VA, this finds every `push imm32` / `mov eax, imm32` that
loads that VA, then walks back to the function prologue (55 8B EC) and reports
the function start, so the parser region can be identified without a disassembler.

Read-only. Usage: python -I scripts/fc3_cmdline_cluster.py <pe file> [switch VA ...]
"""
import struct
import sys

DEFAULT_SWITCH_VAS = None  # filled from --switchs file or arg list


def load(path):
    d = open(path, "rb").read()
    pe = struct.unpack_from("<I", d, 0x3c)[0]
    nsec = struct.unpack_from("<H", d, pe + 6)[0]
    ep = struct.unpack_from("<I", d, pe + 24 + 16)[0]
    base = struct.unpack_from("<I", d, pe + 24 + 28)[0]
    magic = struct.unpack_from("<H", d, pe + 24)[0]
    opt = 224 if magic == 267 else 240
    secs = {}
    so = pe + 24 + opt
    for i in range(nsec):
        nm = d[so + i * 40:so + i * 40 + 8].rstrip(b"\0").decode(errors="replace")
        vs, va, rs, rp = struct.unpack_from("<IIII", d, so + i * 40 + 8)
        secs[nm] = (base + va, vs, rs, rp)
    return d, ep, base, secs


def va2off(secs, va):
    for nm, (sva, vs, rs, rp) in secs.items():
        if sva <= va < sva + max(vs, rs) and va - sva < rs:
            return rp + (va - sva)


def off2va(secs, off):
    for nm, (sva, vs, rs, rp) in secs.items():
        if rp <= off < rp + rs:
            return sva + (off - rp)


PROLOGUES = (b"\x55\x8b\xec", b"\x55\x81\xec", b"\x55\x8b\xf1", b"\xcc\x55\x8b\xec")


def func_start(d, off, window=0x4000):
    """Walk back from off to the nearest function prologue, return file offset."""
    lo = max(0, off - window)
    best = None
    for pr in PROLOGUES:
        k = d.rfind(pr, lo, off)
        while k >= 0:
            if best is None or k > best:
                best = k
            k = d.rfind(pr, lo, k - 1)
        if best is not None:
            break
    return best


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    path = sys.argv[1]
    vas = [int(a, 16) for a in sys.argv[2:]]
    if not vas:
        print("need at least one switch VA (hex)")
        return 2
    d, ep, base, secs = load(path)
    tva, tvs, trs, trp = secs[".text"]
    tstart, tend = trp, trp + trs
    print("file=%s base=%08x EP=%08x .text raw=%08x..%08x VA=%08x" %
          (path, base, ep, tstart, tend, tva))
    funcs = {}
    for va in vas:
        needle = struct.pack("<I", va)
        off = va2off(secs, va)
        if off is None:
            print("switch VA %08x: not mapped in file" % va)
            continue
        print("switch VA %08x raw=%08x str=%r" % (va, off, d[off:off + 24].split(b"\0")[0]))
        sites = []
        k = d.find(needle, tstart, tend)
        while k >= 0:
            op = d[k - 1]
            if op in (0x68, 0xb8, 0xba, 0x3d):
                sites.append((k - 1, op))
            k = d.find(needle, k + 1, tend)
        for site, op in sites:
            fs = func_start(d, site)
            fva = off2va(secs, fs) if fs is not None else None
            funcs.setdefault(fva, []).append("%08x(op=%02x)" % (off2va(secs, site), op))
            print("   ref %08x op=%02x -> func %s ctx=%s" %
                  (off2va(secs, site), op, "%08x" % fva if fva else "?",
                   d[site - 12:site + 9].hex(" ")))
    print("\nfunctions touching these switches (%d):" % len(funcs))
    for fva in sorted(funcs, key=lambda v: (v is None, v or 0)):
        refs = funcs[fva]
        print("  %s  %d refs: %s" % ("%08x" % fva if fva else "?", len(refs), ", ".join(refs)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
