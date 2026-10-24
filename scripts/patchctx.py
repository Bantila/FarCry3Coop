"""Show context for every byte run that differs between two same-size PE files."""
import struct, sys, re

a = open(sys.argv[1], "rb").read()
b = open(sys.argv[2], "rb").read()
pe = struct.unpack_from("<I", a, 0x3C)[0]
nsec = struct.unpack_from("<H", a, pe + 6)[0]
image_base = struct.unpack_from("<I", a, pe + 24 + 28)[0]
sec_off = pe + 24 + struct.unpack_from("<H", a, pe + 20)[0]
sections = []
for i in range(nsec):
    name = a[sec_off + i * 40: sec_off + i * 40 + 8].rstrip(b"\0").decode()
    vsize, vaddr, rsize, rptr = struct.unpack_from("<IIII", a, sec_off + i * 40 + 8)
    sections.append((name, vaddr, rsize, rptr))


def va(off):
    for name, vaddr, rsize, rptr in sections:
        if rptr <= off < rptr + rsize:
            return name, image_base + vaddr + off - rptr
    return "?", 0


runs, i = [], 0
while i < len(a):
    if a[i] != b[i]:
        j = i
        while j < len(a) and a[j] != b[j]:
            j += 1
        runs.append((i, j))
        i = j
    else:
        i += 1

printable = re.compile(rb"[\x20-\x7e]{4,}")
for i, j in runs:
    sec, addr = va(i)
    lo, hi = (i - 16) & ~3, ((j + 16) + 3) & ~3
    line = f"file+0x{i:08x} {sec} va 0x{addr:08x} len {j - i}: {a[i:j].hex()} -> {b[i:j].hex()}"
    if sec != ".text":
        fa = [struct.unpack_from("<f", a, k)[0] for k in range(lo, hi, 4)]
        fb = [struct.unpack_from("<f", b, k)[0] for k in range(lo, hi, 4)]
        changed = [(f"{x:g}", f"{y:g}") for x, y in zip(fa, fb) if x != y]
        line += f"\n    floats changed: {changed}"
        sa = [m.group().decode() for m in printable.finditer(a[i - 48: j + 48])]
        sb = [m.group().decode() for m in printable.finditer(b[i - 48: j + 48])]
        if sa != sb:
            line += f"\n    strings: {sa} -> {sb}"
    else:
        line += f"\n    code: {a[i - 8: j + 8].hex()}"
    print(line)
