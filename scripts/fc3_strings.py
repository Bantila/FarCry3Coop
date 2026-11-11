"""Find launcher/re-exec related strings in a Far Cry 3 PE file and who references them.

Read-only. Usage: python -I scripts/fc3_strings.py <pe file> [regex ...]
Default regexes cover the Uplay launch chain: command-line building, registry
StartArguments, upc_* ids, -language handling.

"""
import re as _re
import struct
import sys


DEFAULT_PATTERNS = [
    r"language", r"StartArguments", r"upc_", r"-exec", r"video_setmode",
    r"desktop_mode", r"game_starter", r"uplay_id", r"\\bin\\", r"\.exe",
]


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


def scan_strings(d, secs, patterns):
    out = []
    for nm, (sva, vs, rs, rp) in secs.items():
        if nm not in (".rdata", ".data", ".text"):
            continue
        blob = d[rp:rp + rs]
        for m in _re.finditer(rb"[\x20-\x7e]{4,}", blob):
            s = m.group().decode("ascii")
            if any(_re.search(p, s, _re.I) for p in patterns):
                out.append((nm, off2va(secs, rp + m.start()), rp + m.start(), s))
        for m in _re.finditer(rb"(?:[\x20-\x7e]\x00){4,}", blob):
            s = m.group().decode("utf-16-le")
            if any(_re.search(p, s, _re.I) for p in patterns):
                out.append((nm + " (utf16)", off2va(secs, rp + m.start()), rp + m.start(), s))
    return out


def refs_for(d, secs, va):
    """push imm32 / mov r32,imm32 loading this VA inside .text."""
    needle = struct.pack("<I", va)
    tva, tvs, trs, trp = secs[".text"]
    hits = []
    k = d.find(needle, trp, trp + trs)
    while k >= 0:
        if k > trp and d[k - 1] in (0x68, 0xb8, 0xba, 0x3d, 0x05):
            hits.append(off2va(secs, k - 1))
        k = d.find(needle, k + 1, trp + trs)
    return hits


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    path = sys.argv[1]
    pats = sys.argv[2:] or DEFAULT_PATTERNS
    d, base, secs = load(path)
    print("file=%s patterns=%s" % (path, pats))
    hits = scan_strings(d, secs, pats)
    print("strings matched: %d" % len(hits))
    seen = set()
    for nm, va, raw, s in hits:
        if va in seen:
            continue
        seen.add(va)
        rr = refs_for(d, secs, va)
        print("%08x raw=%08x [%s] %r refs=%s" %
              (va, raw, nm, s[:90], ", ".join("%08x" % v for v in rr[:8]) or "-"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
