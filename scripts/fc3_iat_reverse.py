"""Reverse-map IAT slots: given thunk addresses, print the imported DLL+function name.

Read-only. Usage: python -I tools/fc3_iat_reverse.py <pe file> [0xVA ...]
"""
import struct
import sys

sys.path.insert(0, r"D:/Projects/Co-op Anything/FarCry3Coop-bantila/scripts")
from fc3_addrmap import PE  # noqa: E402


def clean(s):
    return "".join(ch if 0x20 <= ord(ch) < 0x7F else "." for ch in s)


def build_map(path):
    pe = PE(path)
    d = pe.d
    peoff = struct.unpack_from("<I", d, 0x3C)[0]
    opt = struct.unpack_from("<H", d, peoff + 20)[0]
    dd = peoff + 24 + (96 if opt == 224 else 88)
    imp_rva, imp_size = struct.unpack_from("<II", d, dd + 8)
    k = pe.va2off(pe.base + imp_rva)
    table = {}
    n = 0
    while n < 100:
        ilt_rva, ts, fwd, name_rva, thilt_rva = struct.unpack_from("<IIIII", d, k)
        if name_rva == 0 and ilt_rva == 0 and thilt_rva == 0:
            break
        no = pe.va2off(pe.base + name_rva)
        dll = clean(d[no:d.index(b"\0", no)].decode(errors="replace")) if no is not None else "?"
        for rva in (ilt_rva, thilt_rva):
            if not rva:
                continue
            tbl = pe.va2off(pe.base + rva)
            cnt, j = 0, tbl
            while cnt < 6000:
                val = struct.unpack_from("<I", d, j)[0]
                if val == 0:
                    break
                if val & 0x80000000:
                    table[pe.base + rva + cnt * 4] = "%s:#%d" % (dll, val & 0xFFFF)
                else:
                    nn = pe.va2off(pe.base + val) + 2
                    table[pe.base + rva + cnt * 4] = "%s:%s" % (dll, clean(d[nn:d.index(b"\0", nn)].decode(errors="replace")))
                cnt += 1
                j += 4
        n += 1
        k += 20
    return pe, table


if __name__ == "__main__":
    args = sys.argv[1:]
    path = args[0]
    targets = [int(a, 16) for a in args[1:]]
    pe, table = build_map(path)
    print("== %s : %d IAT slots mapped" % (path, len(table)))
    if not targets:
        for va in sorted(table):
            print("  0x%08x %s" % (va, table[va]))
    for t in targets:
        print("  0x%08x -> %s" % (t, table.get(t, "UNKNOWN (not an IAT slot)")))
