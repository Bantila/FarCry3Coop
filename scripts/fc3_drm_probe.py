"""Read-only DRM/UPC bootstrap probe for Far Cry 3 1.06 binaries.

Usage: python -I scripts/fc3_drm_probe.py [--dll PATH] [--upc PATH] [--exe PATH]
Default targets: FC3_d3d11.dll, upc_r1_loader.dll, farcry3_d3d11.exe, FC3Updater.exe
Outputs: IAT thunks + FF15 call sites, string search (ASCII + UTF16LE), code refs,
containing-function detection, entry-stub hex, export-stub hex.
"""
import struct
import sys

BIN = "H:/FarCryCoop/TestFC3/bin/"


class PE(object):
    def __init__(self, path):
        self.path = path
        self.d = open(path, "rb").read()
        nt = struct.unpack_from("<I", self.d, 0x3C)[0]
        self.nt = nt
        optsize = struct.unpack_from("<H", self.d, nt + 20)[0]
        self.optsize = optsize
        self.magic = struct.unpack_from("<H", self.d, nt + 24)[0]
        self.base = struct.unpack_from("<I", self.d, nt + 24 + 28)[0]
        self.ep = struct.unpack_from("<I", self.d, nt + 24 + 16)[0]
        nsec = struct.unpack_from("<H", self.d, nt + 6)[0]
        so = nt + 24 + optsize
        self.sec = []
        self.exec_ranges = []
        for i in range(nsec):
            rec = so + i * 40
            nm = self.d[rec:rec + 8].rstrip(b"\0").decode(errors="replace")
            vs, va, rs, rp = struct.unpack_from("<IIII", self.d, rec + 8)
            fl = struct.unpack_from("<I", self.d, rec + 36)[0]
            self.sec.append((nm, self.base + va, vs, rs, rp, fl))
            if fl & 0xE0000000 == 0x80000000 or fl & 0x20000000:
                self.exec_ranges.append((self.base + va, rp, rs))
        self.dd = nt + 24 + optsize - 128
        tva, tsize, tptr = None, None, None
        for nm, va, vs, rs, rp, fl in self.sec:
            if nm == ".text":
                tva, tsize, tptr = va, rs, rp
        self.text = (tva, tva + tsize, tptr, tsize)

    def off2va(self, off):
        for nm, va, vs, rs, rp, fl in self.sec:
            if rp <= off < rp + rs:
                return va + off - rp
        return None

    def va2off(self, va):
        for nm, va2, vs, rs, rp, fl in self.sec:
            if va2 <= va < va2 + rs:
                return rp + va - va2
        return None

    def in_exec(self, va):
        for a, rp, span in self.exec_ranges:
            if a <= va < a + span:
                return True
        return False

    def dd_get(self, i):
        return struct.unpack_from("<II", self.d, self.dd + i * 8)

    def imports(self):
        rva, size = self.dd_get(1)
        o = self.va2off(self.base + rva)
        out = []
        n = 0
        while True:
            ilt, t1, fwd, nrva, thilt = struct.unpack_from("<IIIII", self.d, o + n * 20)
            if ilt == 0 and nrva == 0 and thilt == 0:
                break
            no = self.va2off(self.base + nrva)
            e = self.d.find(b"\0", no)
            dll = self.d[no:e].decode(errors="replace")
            tbl = self.va2off(self.base + (thilt or ilt))
            entries = []
            i = 0
            while True:
                v = struct.unpack_from("<I", self.d, tbl + i * 4)[0]
                if v == 0:
                    break
                if v & 0x80000000:
                    name = "ord#%d" % (v & 0xFFFF)
                else:
                    p = self.va2off(self.base + v + 2)
                    e2 = self.d.find(b"\0", p)
                    name = self.d[p:e2].decode(errors="replace")
                entries.append((self.base + (thilt or ilt) + i * 4, name))
                i += 1
            out.append((dll, entries))
            n += 1
        return out

    def thunk_of(self, name):
        res = []
        for dll, entries in self.imports():
            for va, nm in entries:
                if nm == name:
                    res.append((dll, va))
        return res

    def str_at(self, off):
        e = self.d.find(b"\0", off)
        return self.d[off:e].decode(errors="replace")

    def cstrings(self, s):
        b = s.encode("ascii")
        out = []
        i = 0
        while True:
            j = self.d.find(b, i)
            if j < 0:
                break
            ok_end = (j + len(b) < len(self.d) and self.d[j + len(b)] == 0)
            ok_start = (j == 0 or self.d[j - 1] == 0)
            if ok_end and ok_start:
                out.append((j, self.off2va(j)))
            i = j + 1
        return out

    def rawfind(self, b):
        out = []
        i = 0
        while True:
            j = self.d.find(b, i)
            if j < 0:
                break
            out.append((j, self.off2va(j)))
            i = j + 1
        return out

    def hexat(self, off, before=24, after=16):
        a = max(0, off - before)
        return self.d[a:off + after].hex(" ")


def call_sites(pe, thunk_va):
    """all FF 15 <thunk LE> (call [IAT]) and FF 25 <thunk LE> (jmp [IAT]) across exec sections"""
    pat = struct.pack("<I", thunk_va)
    sites = []
    for a, rp, span in pe.exec_ranges:
        seg = pe.d[rp:rp + span]
        i = 0
        while True:
            j = seg.find(b"\xff", i)
            if j < 0:
                break
            if j + 6 <= len(seg) and seg[j + 1] in (0x15, 0x25, 0x1D, 0x2D) and seg[j + 2:j + 6] == pat:
                va = a + j
                off = rp + j
                pushimm = None
                k = j - 1
                for _ in range(10):
                    if k < 0:
                        break
                    if seg[k] == 0x68 and k + 5 <= len(seg):
                        imm = struct.unpack_from("<I", seg, k + 1)[0]
                        if pe.va2off(imm) is not None:
                            o = pe.va2off(imm)
                            s = pe.str_at(o)
                            if s:
                                pushimm = (a + k, imm, s)
                                break
                    k -= 1
                sites.append((va, off, seg[j] == 0x15 and "call" or "jmp", pushimm))
            i = j + 1
    return sites


def refs_to(pe, va, sections_only_exec=True):
    """imm32 references to VA preceded by 0x68 (push) or 0xB8-0xBF (mov reg) or 0x8D/0x89/0xC7/0xA1"""
    pat = struct.pack("<I", va)
    out = []
    ranges = pe.exec_ranges if sections_only_exec else [(sec[1], sec[4], sec[3]) for sec in pe.sec]
    for a, rp, span in ranges:
        seg = pe.d[rp:rp + span]
        i = 0
        while True:
            j = seg.find(pat, i)
            if j < 0:
                break
            if j > 0:
                prev = seg[j - 1]
                if prev == 0x68 or (0xB8 <= prev <= 0xBF) or prev in (0x8D, 0x89, 0xC7, 0xA1, 0x3D, 0x6A):
                    out.append((a + j - 1, rp + j - 1, prev))
            i = j + 1
    return out


PROLOGS = [b"\x55\x8b\xec", b"\x55\x8b\xee", b"\x56\x57", b"\x53\x56\x57", b"\x55\x33\xc0", b"\x55\xff", b"\x55\xe8"]


def find_func(pe, va, maxback=0x600):
    """scan backwards for a plausible function prologue preceded by CC/90 padding"""
    off = pe.va2off(va)
    if off is None:
        return None
    for k in range(off, max(0, off - maxback), -1):
        for p in PROLOGS:
            if pe.d[k:k + len(p)] == p:
                prev = pe.d[k - 1] if k > 0 else 0
                if prev in (0xCC, 0x90, 0xC3) or pe.d[k - 2:k] in (b"\xcc\xcc",):
                    return pe.off2va(k)
    return None


def show_string_search(pe, keys, maxhits=25, code_ref_limit=12):
    print("### STRING SEARCH in %s" % pe.path)
    for k in keys:
        hits = pe.cstrings(k)
        hits16 = pe.rawfind(k.encode("utf-16-le"))
        print("  %-24s ascii=%3d  utf16=%3d" % (k, len(hits), len(hits16)))
        for (o, v) in hits[:maxhits]:
            refs = refs_to(pe, v) if v else []
            print("     raw=0x%08x va=%s  code_refs=%d" % (o, "0x%08x" % v if v else "unmapped", len(refs)))
            for (rv, ro, op) in refs[:code_ref_limit]:
                f = find_func(pe, rv)
                print("        ref@0x%08x op=0x%02x func=%s ctx=%s" % (rv, op, ("0x%08x" % f) if f else "?", pe.hexat(ro, 6, 10)))
        for (o, v) in hits16[:12]:
            refs = refs_to(pe, v) if v else []
            print("     UTF16 raw=0x%08x va=%s refs=%d" % (o, "0x%08x" % v if v else "unmapped", len(refs)))


def show_thunks(pe, names, maxsites=40):
    print("### IAT THUNKS + CALL SITES in %s" % pe.path)
    for n in names:
        for dll, tv in pe.thunk_of(n):
            sites = call_sites(pe, tv)
            print("  %-24s (%s) thunk=0x%08x sites=%d" % (n, dll, tv, len(sites)))
            for (va, off, kind, pi) in sites[:maxsites]:
                f = find_func(pe, va)
                s = pi[2] if pi else ""
                print("     %s @0x%08x func=%s push=%s ctx=%s" % (kind, va,
                      ("0x%08x" % f) if f else "?", s, pe.hexat(off, 20, 10)))


def dump(pe, va, n, label=""):
    off = pe.va2off(va)
    print("  %s @0x%08x raw=0x%x: %s" % (label, va, off, pe.d[off:off + n].hex(" ")))

BIN = "H:/FarCryCoop/TestFC3/bin/"
KEYS = ["ExecutableName", "InstallDir", "SKU", "Version", "Language", "WOW6432Node",
"SOFTWARE\\Ubisoft", "Far Cry 3", "farcry3.exe", "farcry3_d3d11.exe", "Farcry3.exe",
"Farcry3_d3d11.exe", "FC3Updater", "bin/farcry3", "bin/FC3", "upc_r1_loader", "upc_r1",
"upc.ini", "CreateProcess", "ShellExecute", "RunGame", "-language", "-host", "My Games",
"uplay", "Uplay", "UbisoftGameLauncher", "SteamService", "steam_api", "online", "Online"]

if __name__ == "__main__":
    tgt = sys.argv[1] if len(sys.argv) > 1 else BIN + "FC3_d3d11.dll"
    pe = PE(tgt)
    print("=== %s base=0x%08x entry=0x%08x text=0x%08x-0x%08x" %
          (pe.path, pe.base, pe.base + pe.ep, pe.text[0], pe.text[1]))
    for sec in pe.sec:
        print("   sec %-9s va=0x%08x rsize=0x%08x rptr=0x%08x flags=0x%08x" % (sec[0], sec[1], sec[3], sec[4], sec[5]))
    dump(pe, pe.base + pe.ep, 40, "ENTRY")
    show_thunks(pe, ["LoadLibraryA", "LoadLibraryW", "LoadLibraryExW", "GetProcAddress",
                     "FreeLibrary", "GetModuleHandleA", "GetModuleHandleExA", "GetModuleHandleW",
                     "ShellExecuteA", "ShellExecuteW", "SHGetFolderPathW", "GetModuleFileNameA",
                     "GetModuleFileNameW", "OpenMutexA", "CreateMutexA", "RegOpenKeyA",
                     "RegOpenKeyExA", "RegQueryValueExA", "RegCloseKey", "RegisterEventSourceA"])
    show_string_search(pe, KEYS)
