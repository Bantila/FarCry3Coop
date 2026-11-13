"""Resolve PE import thunks (IAT entries) and every code call site through them.

Read-only. Finds where OpenMutexA / CreateMutexA / ShellExecuteA / registry APIs are called
in a given FC3 build, and dumps the raw bytes around each call site.

Usage: python -I scripts/fc3_iat_scan.py <pe file> [ImportName ...]
"""
import re
import struct
import sys

sys.path.insert(0, r"D:/Projects/Co-op Anything/FarCry3Coop-bantila/scripts")
from fc3_addrmap import PE  # noqa: E402

DEFAULTS = ["OpenMutexA", "CreateMutexA", "ShellExecuteA", "ShellExecuteW", "CreateProcessA",
            "CreateProcessW", "RegOpenKeyExA", "RegQueryValueExA", "WinExec"]


def clean(s):
    return "".join(ch if 0x20 <= ord(ch) < 0x7F else "." for ch in s)


def iat_scan(path, names):
    pe = PE(path)
    d = pe.d
    peoff = struct.unpack_from("<I", d, 0x3C)[0]
    opt = struct.unpack_from("<H", d, peoff + 20)[0]
    nsec = struct.unpack_from("<H", d, peoff + 6)[0]
    so = peoff + 24 + opt
    secs = []
    for i in range(nsec):
        nm = d[so + i * 40: so + i * 40 + 8].rstrip(b"\0").decode(errors="replace")
        vs, va, rs, rp = struct.unpack_from("<IIII", d, so + i * 40 + 8)
        secs.append((nm, pe.base + va, vs, rs, rp))

    # data directory #1 (import) sits at optional-header offset 96 (PE32+) or 88 (PE32)
    dd = peoff + 24 + (96 if opt == 224 else 88)
    imp_rva, imp_size = struct.unpack_from("<II", d, dd + 8)
    print("== %s base=0x%x import dir rva=0x%08x size=%d" % (path, pe.base, imp_rva, imp_size))
    if not imp_rva:
        print("   no import directory")
        return
    k = pe.va2off(pe.base + imp_rva)
    if k is None:
        print("   import dir unmapped")
        return
    thunks = {}
    ndll = 0
    while True:
        ilt_rva, ts, fwd, name_rva, thilt_rva = struct.unpack_from("<IIIII", d, k)
        if name_rva == 0 and ilt_rva == 0 and thilt_rva == 0:
            break
        no = pe.va2off(pe.base + name_rva)
        dll = clean(d[no:d.index(b"\0", no)].decode(errors="replace")) if no is not None else "?"
        tbl = pe.va2off(pe.base + (thilt_rva or ilt_rva))
        cnt = 0
        j = tbl
        while True:
            val = struct.unpack_from("<I", d, j)[0]
            if val == 0:
                break
            if not (val & 0x80000000):
            # noqa: E111 - name table entry
                nn = pe.va2off(pe.base + val) + 2
                nm = clean(d[nn:d.index(b"\0", nn)].decode(errors="replace"))
                if nm in names:
                    thunk_va = pe.base + (thilt_rva or ilt_rva) + cnt * 4
                    thunks.setdefault(nm, []).append((dll, thunk_va))
            cnt += 1
            j += 4
            if cnt > 4000:
                break
        ndll += 1
        k += 20
        if ndll > 100:
            break
    print("   %d imported DLLs" % ndll)
    for nm in names:
        for dll, thunk in thunks.get(nm, []):
            needle = struct.pack("<I", thunk)
            tva, tend, tptr, tsize = pe.text
            text = d[tptr:tptr + tsize]
            sites = []
            i = text.find(needle)
            while i >= 0:
                if i >= 1 and text[i - 1] == 0xFF and text[i] in (0x15, 0x25):
                    sites.append(tva + i - 1)
                elif i >= 2 and text[i - 2] == 0xFF and text[i - 1] in (0x15, 0x25):
                    sites.append(tva + i - 2)
                i = text.find(needle, i + 1)
            print("  %-16s (%s) thunk 0x%08x call sites (%d): %s" % (
                nm, dll, thunk, len(sites), ", ".join("0x%08x" % s for s in sites[:10])))
            for s in sites[:6]:
                off = pe.va2off(s)
                seg = d[off - 20:off + 16]
                print("      0x%08x ctx %s" % (s, " ".join("%02X" % b for b in seg)))


if __name__ == "__main__":
    args = sys.argv[1:]
    for p in args[1:] or [r"H:/FarCryCoop/TestFC3/bin/FC3_d3d11.dll"]:
        pass
    if args:
        iat_scan(args[0], args[1:] or DEFAULTS)
    else:
        iat_scan(r"H:/FarCryCoop/TestFC3/bin/FC3_d3d11.dll", DEFAULTS)
