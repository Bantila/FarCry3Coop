"""Find every caller of a function in a Far Cry 3 PE file (read-only).

Searches .text for `e8 <rel32>` calls whose target matches the function VA, and
for absolute 4-byte references (vtables / jump tables) to it.

Usage: python -I tools/fc3_callers.py <pe file> <func VA hex> [more VA hex ...]
"""
import re as _re
import struct
import sys


def load(path):
    d = open(path, "rb").read()
    pe = struct.unpack_from("<I", d, 0x3c)[0]
    nsec = struct.unpack_from("<H", d, pe + 6)[0]
    base = struct.unpack_from("<I", d, pe + 24 + 28)[0]
    magic = struct.unpack_from("<H", d, pe + 24)[0]
    opt = 224 if magic == 267 else 240
    secs = {}
    so = pe + 24 + opt
    for i in range(nsec):
        nm = d[so + i * 40:so + i * 40 + 8].rstrip(b"\0").decode(errors="replace")
        vs, va, rs, rp = struct.unpack_from("<IIII", d, so + i * 40 + 8)
        secs[nm] = (base + va, vs, rs, rp)
    return d, base, secs


def off2va(secs, off):
    for nm, (sva, vs, rs, rp) in secs.items():
        if rp <= off < rp + rs:
            return sva + (off - rp)


def func_end(d, off, limit=0x2000):
    """Crude function end: first int3 padding run followed by a new prologue."""
    k = off
    end = off + limit
    while k < off + limit:
        idx = d.find(b"\xcc\xcc", k)
        if idx < 0 or idx >= off + limit:
            break
        nxt = d[idx:idx + 12].find(b"\x55\x8b\xec")
        if nxt >= 0:
            end = idx
            break
        k = idx + 2
    return end


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        return 2
    path = sys.argv[1]
    targets = [int(a, 16) for a in sys.argv[2:]]
    d, base, secs = load(path)
    tva, tvs, trs, trp = secs[".text"]
    tstart, tend = trp, trp + trs
    print("file=%s base=%08x .text VA=%08x raw=%08x..%08x" % (path, base, tva, tstart, tend))
    # One pass over .text collecting every E8 call target (call VA -> call site raw).
    CALLS = {}
    text_bytes = d[tstart:tend]
    for m in _re.finditer(b"\xe8", text_bytes):
        i = tstart + m.start()
        if i + 5 > tend:
            continue
        rel = struct.unpack_from("<i", d, i + 1)[0]
        site_va = off2va(secs, i)
        if site_va is None:
            continue
        CALLS.setdefault(site_va + 5 + rel, []).append(site_va)
    for tv in targets:
        rel_off = tv2off = None
        callers, absolues = [], []
        # relative E8 calls
        found = CALLS.get(tv, [])
        # absolute references anywhere in the file
        needle = struct.pack("<I", tv)
        k = d.find(needle)
        while k >= 0:
            if off2va(secs, k) != tv:  # skip the raw bytes of the string itself etc.
                absolues.append((off2va(secs, k), k))
            k = d.find(needle, k + 1)
        print("\ntarget %08x: %d E8 callers" % (tv, len(found)))
        for site in found[:24]:
            o = va2off(secs, site)
            print("   caller site %08x ctx=%s" % (site, d[o - 14:o + 9].hex(" ")))
        print("   absolute refs (%d): %s" % (len(absolues),
              ", ".join("%s(raw=%x)" % ("%08x" % v if v else "-", r) for v, r in absolues[:16])))
    return 0


def va2off(secs, va):
    for nm, (sva, vs, rs, rp) in secs.items():
        if sva <= va < sva + max(vs, rs) and va - sva < rs:
            return rp + (va - sva)


if __name__ == "__main__":
    sys.exit(main())
