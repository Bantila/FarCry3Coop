"""Hex/ASCII dump of a VA range in a Far Cry 3 PE file, plus prologue detection.

Read-only. Usage: python -I scripts/fc3_dump.py <pe file> <VA hex> [length] [--back]
  --back  : also locate the function start (nearest 55 8B EC style prologue) before the VA
            and dump from there.
"""
import re as _re
import struct
import sys

PROLOGUES = (b"\x55\x8b\xec", b"\x55\x81\xec", b"\x55\x8b\xf1", b"\xcc\x55\x8b\xec")
R32 = ["eax", "ecx", "edx", "ebx", "esp", "ebp", "esi", "edi"]


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


def va2off(secs, va):
    for nm, (sva, vs, rs, rp) in secs.items():
        if sva <= va < sva + max(vs, rs) and va - sva < rs:
            return rp + (va - sva)


def off2va(secs, off):
    for nm, (sva, vs, rs, rp) in secs.items():
        if rp <= off < rp + rs:
            return sva + (off - rp)


def func_start(d, off, window=0x6000):
    best = None
    for pr in PROLOGUES:
        k = d.rfind(pr, max(0, off - window), off)
        while k >= 0:
            if best is None or k > best:
                best = k
            k = d.rfind(pr, max(0, off - window), k - 1)
        if best is not None:
            break
    return best


def annotate(d, off, base_va):
    """Print a crude single-instruction decode at off (enough to read arg pushes)."""
    b = d[off]
    va = off2va_ = None
    if b == 0x68:
        imm = struct.unpack_from("<I", d, off + 1)[0]
        return 5, "push 0x%08x" % imm
    if b == 0xe8:
        rel = struct.unpack_from("<i", d, off + 1)[0]
        return 5, "call 0x%08x" % (off2va(SECS, off) + 5 + rel) if SECS else "call ?"
    if b in (0x50 + 0,) and False:
        pass
    if 0x50 <= b <= 0x57:
        return 1, "push %s" % R32[b - 0x50]
    if 0x58 <= b <= 0x5f:
        return 1, "pop %s" % R32[b - 0x58]
    if b == 0xff and d[off + 1] in (0xd6, 0xd7, 0xc3, 0xc0, 0xe0, 0xe1, 0xe2, 0xe3, 0xe6, 0xe7):
        reg = {0xd6: "esi", 0xd7: "edi", 0xc3: "ebx", 0xc0: "eax", 0xe0: "eax",
               0xe1: "ecx", 0xe2: "edx", 0xe3: "ebx", 0xe6: "ebp", 0xe7: "esp"}[d[off + 1]]
        return 2, "call %s" % reg
    if b == 0x8b and d[off + 1] == 0x3d:
        imm = struct.unpack_from("<I", d, off + 2)[0]
        return 6, "mov edi,[0x%08x]" % imm
    if b == 0x8b and d[off + 1] == 0x35:
        imm = struct.unpack_from("<I", d, off + 2)[0]
        return 6, "mov esi,[0x%08x]" % imm
    if b == 0x8b and d[off + 1] == 0x0d:
        imm = struct.unpack_from("<I", d, off + 2)[0]
        return 6, "mov ecx,[0x%08x]" % imm
    if b == 0x8b and d[off + 1] == 0x15:
        imm = struct.unpack_from("<I", d, off + 2)[0]
        return 6, "mov edx,[0x%08x]" % imm
    if b == 0x8b and d[off + 1] == 0x1d:
        imm = struct.unpack_from("<I", d, off + 2)[0]
        return 6, "mov ebx,[0x%08x]" % imm
    if b == 0x8b and d[off + 1] == 0x3d:
        imm = struct.unpack_from("<I", d, off + 2)[0]
        return 6, "mov edi,[0x%08x]" % imm
    if b == 0xe9:
        rel = struct.unpack_from("<i", d, off + 1)[0]
        return 5, "jmp rel -> 0x%08x" % (imm_va(off, rel))
    if b == 0x0f and d[off + 1] in (0x84, 0x85, 0x8b, 0x8e):
        rel = struct.unpack_from("<i", d, off + 2)[0]
        cc = {0x84: "z", 0x85: "nz", 0x8b: "s", 0x8e: "le"}[d[off + 1]]
        return 6, "j%s 0x%08x" % (cc, imm_va(off, rel))
    if b == 0x74 or b == 0x75:
        rel = struct.unpack_from("<b", d, off + 1)[0]
        return 2, "j%s rel %+d" % ("z" if b == 0x74 else "nz", rel)
    return 1, "%02x" % b


def imm_va(off, rel):
    v = off2va(SECS, off)
    return (v + 5 + rel) if v else 0


def main():
    global SECS
    if len(sys.argv) < 3:
        print(__doc__)
        return 2
    path, va_s = sys.argv[1], int(sys.argv[2], 16)
    length = int(sys.argv[3], 0) if len(sys.argv) > 3 and sys.argv[3].isdigit() else 0x180
    back = "--back" in sys.argv
    d, base, SECS = load(path)
    off = va2off(SECS, va_s)
    if off is None:
        print("VA %08x not mapped" % va_s)
        return 2
    start_off = off
    if back:
        fs = func_start(d, off)
        if fs is not None:
            start_off = fs
            print("func start VA %08x (raw %08x), requested %08x" %
                  (off2va(SECS, fs), fs, va_s))
    cur = start_off
    end = start_off + length
    while cur < end:
        n, txt = annotate(d, cur, base)
        print("%08x  %s  [%s]" % (off2va(SECS, cur), d[cur:cur + min(n, 8)].hex(" "), txt))
        cur += n
    return 0


SECS = None

if __name__ == "__main__":
    sys.exit(main())
