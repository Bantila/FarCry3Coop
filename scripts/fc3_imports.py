"""Dump the PE import directory of FC3 binaries (read-only).

Usage: python -I scripts/fc3_imports.py <pe file> [more files...]
"""
import struct
import sys


def imports(path):
    d = open(path, "rb").read()
    pe = struct.unpack_from("<I", d, 0x3C)[0]
    opt = struct.unpack_from("<H", d, pe + 20)[0]
    ep = struct.unpack_from("<I", d, pe + 24 + 16)[0]
    base = struct.unpack_from("<I", d, pe + 24 + 28)[0]
    nsec = struct.unpack_from("<H", d, pe + 6)[0]
    so = pe + 24 + opt
    secs = []
    for i in range(nsec):
        nm = d[so + i * 40: so + i * 40 + 8].rstrip(b"\0").decode(errors="replace")
        vs, va, rs, rp = struct.unpack_from("<IIII", d, so + i * 40 + 8)
        secs.append((nm, base + va, vs, rs, rp))

    def off2va(off):
        for nm, va, vs, rs, rp in secs:
            if rp <= off < rp + rs:
                return va + off - rp
        return None

    def va2off(va):
        for nm, va2, vs, rs, rp in secs:
            if va2 <= va < va2 + max(vs, rs):
                return rp + va - va2
        return None

    # data directories: import table is entry #1 of the optional header RVAs
    dd_off = pe + 24 + 96 * 8 if opt == 224 else pe + 24 + 112 * 8
    # locate the import directory by scanning known optional-header layout: index 1
    imp_rva = struct.unpack_from("<I", d, pe + 24 + (96 if opt == 224 else 88) + 8)[0]
    print("%s EP=0x%08x base=0x%x optsz=%d" % (path, ep, base, opt))
    for nm, va, vs, rs, rp in secs:
        print("  sec %-8s va=0x%08x vsize=%d rsize=%d raw=0x%06x" % (nm, va, vs, rs, rp))
    imp_off = va2off(base + imp_rva) if imp_rva else None
    print("  import dir rva=0x%08x raw=%s" % (imp_rva, hex(imp_off) if imp_off else "None"))
    if imp_off is None:
        return
    k = imp_off
    for n in range(40):
        ilt_rva, ts, fwd, name_rva, thilt_rva = struct.unpack_from("<IIIII", d, k)
        if name_rva == 0 and ilt_rva == 0 and thilt_rva == 0:
            break
        no = va2off(base + name_rva)
        nm = d[no:d.index(b"\0", no)].decode(errors="replace") if no is not None else "?"
        print("  DLL %s (ilt rva=0x%08x)" % (nm, ilt_rva))
        to = va2off(base + (thilt_rva or ilt_rva))
        names = []
        if to is not None:
            j = to
            while True:
                val = struct.unpack_from("<I", d, j)[0]
                if val == 0:
                    break
                if val & 0x80000000:
                    names.append("ord%d" % (val & 0xFFFF))
                else:
                    nn = va2off(base + val) + 2
                    names.append(d[nn:d.index(b"\0", nn)].decode(errors="replace"))
                j += 4
                if len(names) > 400:
                    break
        print("     %d imports: %s" % (len(names), ", ".join(names[:40])))
        k += 20
    if ep:
        eoff = va2off(base + ep)
        if eoff is not None:
            print("  entry bytes: " + " ".join("%02X" % b for b in d[eoff:eoff + 48]))
            ints = []
            for m in range(eoff, eoff + 64 - 5):
                if d[m] == 0xE8:
                    tgt = struct.unpack_from("<i", d, m + 1)[0]
                    ints.append("call 0x%08x" % ((base + ep + (m - eoff) + 5 + tgt) & 0xFFFFFFFF))
            print("  entry calls: " + ", ".join(ints))


if __name__ == "__main__":
    for p in sys.argv[1:]:
        imports(p)
        print()
