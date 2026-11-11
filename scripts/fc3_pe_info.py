"""Read-only PE header/section/export/import summary for FC3 1.06 binaries.

Usage: python -I scripts/fc3_pe_info.py <pe file> [more files...]
Pure stdout. DataDirectory start = nt + 24 + optsize - 128 (16 entries x 8 bytes).
"""
import os
import struct
import sys

DD_NAMES = ["export", "import", "resource", "exception", "security", "basereloc", "debug",
              "architect", "globalptr", "tls", "loadcfg", "boundimp", "iat", "delayimp",
              "clr", "reserved"]


def sz(d, off):
    e = d.find(b"\0", off)
    return d[off:e].decode(errors="replace") if off is not None else "?"


def parse(path):
    d = open(path, "rb").read()
    print("== %s  filesize=%d" % (path, os.path.getsize(path)))
    e_lfanew = struct.unpack_from("<I", d, 0x3C)[0]
    if d[e_lfanew:e_lfanew + 4] != b"PE\0\0":
        print("   bad PE sig at 0x%x" % e_lfanew)
        return
    nt = e_lfanew
    machine = struct.unpack_from("<H", d, nt + 4)[0]
    nsec = struct.unpack_from("<H", d, nt + 6)[0]
    timestamp = struct.unpack_from("<I", d, nt + 8)[0]
    optsize = struct.unpack_from("<H", d, nt + 20)[0]
    chars = struct.unpack_from("<H", d, nt + 22)[0]
    magic = struct.unpack_from("<H", d, nt + 24)[0]
    ep = struct.unpack_from("<I", d, nt + 24 + 16)[0]
    base = struct.unpack_from("<I", d, nt + 24 + 28)[0]
    # PE32: SizeOfImage@+56 SizeOfHeaders@+60 CheckSum@+64 Subsystem@+68 DllChar@+70
    # PE32+: SizeOfImage@+56 Subsystem@+72 DllChar@+74 (BaseOfData absent)
    if magic == 267:
        secalign, filealign, imgsize = nt + 24 + 32, nt + 24 + 36, nt + 24 + 56
        subsys, dllchars, heapres = nt + 24 + 68, nt + 24 + 70, nt + 24 + 80
    else:
        secalign, filealign, imgsize = nt + 24 + 32, nt + 24 + 36, nt + 24 + 56
        subsys, dllchars, heapres = nt + 24 + 72, nt + 24 + 74, nt + 24 + 84
    print("   nt_off=0x%x machine=0x%04x magic=%s nsec=%d optsize=%d chars=0x%04x timestamp=%d"
          % (nt, machine, {267: "PE32", 523: "PE32+"}.get(magic, magic), nsec, optsize, chars, timestamp))
    print("   base=0x%08x entry_rva=0x%x entry_va=0x%08x sizeimage=0x%x secalign=%d filealign=%d subsystem=%d dllchars=0x%04x heapres=0x%x"
          % (base, ep, base + ep, struct.unpack_from("<I", d, imgsize)[0],
             struct.unpack_from("<I", d, secalign)[0], struct.unpack_from("<I", d, filealign)[0],
             struct.unpack_from("<H", d, subsys)[0], struct.unpack_from("<H", d, dllchars)[0],
             struct.unpack_from("<I", d, heapres)[0]))
    so = nt + 24 + optsize
    secs = []
    for i in range(nsec):
        rec = so + i * 40
        nm = d[rec:rec + 8].rstrip(b"\0").decode(errors="replace")
        vs, va, rs, rp = struct.unpack_from("<IIII", d, rec + 8)
        flags = struct.unpack_from("<I", d, rec + 36)[0]
        secs.append((nm, va, vs, rs, rp, flags))
        print("   %-9s va=0x%08x vsize=0x%08x raw=0x%08x rptr=0x%08x flags=0x%08x %s%s%s"
              % (nm, base + va, vs, rs, rp, flags,
                 "X" if flags & 0x20000000 else "-", "W" if flags & 0x80000000 else "-",
                 "R" if flags & 0x40000000 else "-"))
    last = max([rp + rs for (_, _, _, rp, _, _) in [(a, b, c, d2, e2, f2) for (a, b, c, d2, e2, f2) in secs]] + [0]) if secs else 0
    print("   sum_of_raw_ends=0x%x  gap_to_eof=%d bytes (overlay/appdata)"
          % (max([s[3] + s[4] for s in secs] + [0]), os.path.getsize(path) - max([s[3] + s[4] for s in secs] + [0])))
    ddoff = nt + 24 + optsize - 128
    print("   dd_start=0x%x  NumberOfRvaAndSizes=%d" % (ddoff, struct.unpack_from("<I", d, ddoff - 4)[0]))
    dd = {}
    for i, n in enumerate(DD_NAMES):
        rva, size = struct.unpack_from("<II", d, ddoff + i * 8)
        dd[n] = (rva, size)
        if rva:
            print("   DD %-10s rva=0x%08x size=0x%08x" % (n, rva, size))

    def off2va(off):
        for nm, va, vs, rs, rp, fl in secs:
            if rp <= off < rp + rs:
                return base + va + off - rp
        return None

    def va2off(va):
        for nm, va2, vs, rs, rp, fl in secs:
            if base + va2 <= va < base + va2 + rs:
                return rp + va - (base + va2)
        return None

    erva, esize = dd["export"]
    if erva:
        o = va2off(base + erva)
        print("   EXPORT dir rva=0x%08x raw=0x%x" % (erva, o))
        if o is not None:
            # IMAGE_EXPORT_DIRECTORY: +0 chars +4 tstamp +8 maj +10 min +12 Name
            # +16 OrdinalBase +20 NumberOfFunctions +24 NumberOfNames
            # +28 AddressOfFunctions +32 AddressOfNames +36 AddressOfNameOrdinals
            fl, t1, maj, min_ = struct.unpack_from("<IIHH", d, o + 0)
            lname, org, nfun, nnames = struct.unpack_from("<IIII", d, o + 12)
            lfa, lna, lfo = struct.unpack_from("<III", d, o + 28)
            lp = va2off(base + lname)
            print("   module=%r ordinal_base=%d nfunctions=%d nnames=%d" % (sz(d, lp), org, nfun, nnames))
            fwd = []
            fa_off = va2off(base + lfa)
            na_off = va2off(base + lna)
            no_off = va2off(base + lfo)
            for i in range(nnames):
                nn = struct.unpack_from("<I", d, na_off + i * 4)[0]
                if nn == 0:
                    continue
                nm = sz(d, va2off(base + nn))
                fo = struct.unpack_from("<H", d, no_off + i * 2)[0]
                fv = struct.unpack_from("<I", d, fa_off + fo * 4)[0] if fo < nfun else 0
                isfwd = erva <= fv < erva + esize
                tgt = sz(d, va2off(base + fv)) if isfwd else ""
                if isfwd:
                    fwd.append((nm, tgt))
                print("     #%-3d ord=%-4d rva=0x%08x va=0x%08x %s%s"
                      % (i, org + fo, fv, base + fv, nm, ("  FORWARD-> " + tgt) if isfwd else ""))
            if fwd:
                print("   forwarders: %s" % fwd)
            if nnames == 0:
                print("   (no named exports)")
    imrva, imsize = dd["import"]
    if imrva:
        o = va2off(base + imrva)
        n = 0
        total = 0
        while True:
            ilt, t1, fwd, nrva, thilt = struct.unpack_from("<IIIII", d, o + n * 20)
            if ilt == 0 and nrva == 0 and thilt == 0:
                break
            np = va2off(base + nrva)
            dllname = sz(d, np)
            tbl = va2off(base + (thilt or ilt))
            cnt = 0
            names = []
            while True:
                v = struct.unpack_from("<I", d, tbl + cnt * 4)[0]
                if v == 0:
                    break
                if v & 0x80000000:
                    names.append("ord#%d" % (v & 0xFFFF))
                else:
                    names.append(sz(d, va2off(base + v + 2)))
                cnt += 1
                if cnt > 8000:
                    break
            total += cnt
            print("   IMPORT %-22s (%3d) %s" % (dllname, cnt, ", ".join(names[:45]) + (" ...[%d]" % cnt if cnt > 45 else "")))
            n += 1
            if n > 80:
                break
        print("   %d imported DLLs, %d imports total" % (n, total))


if __name__ == "__main__":
    for p in sys.argv[1:]:
        parse(p)
        print()
