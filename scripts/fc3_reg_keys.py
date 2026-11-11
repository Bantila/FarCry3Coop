"""Far Cry 3: who reads HKCU\\Software\\Ubisoft\\Far Cry 3 (ExecutableName / StartArguments)?

HKCU\\Software\\Ubisoft\\Far Cry 3 on this machine currently holds:
    ExecutableName    REG_SZ  bin/FC3Updater.exe
    StartArguments    REG_SZ  (empty)
HKLM\\SOFTWARE\\WOW6432Node\\Ubisoft\\Far Cry 3: InstallDir, ExecutableName, SKU, Version,
Language; subkey \\GameUpdate: execPath, info, installdir.

This probe searches the binaries for those registry value names (ASCII and UTF-16) and
dumps the ASCII immediates inside the functions that contain the RegXxx call sites found
by the IAT scan.

Usage: python -I scripts/fc3_reg_keys.py [pe ...]
"""
import re
import struct
import sys

sys.path.insert(0, r"D:/Projects/Co-op Anything/FarCry3Coop-bantila/scripts")
from fc3_addrmap import PE  # noqa: E402

BIN = r"H:/FarCryCoop/TestFC3/bin"
DEFAULT = [BIN + "/FC3_d3d11.dll", BIN + "/FC3.dll", BIN + "/upc_r1_loader.dll",
           BIN + "/FC3Updater.exe", BIN + "/farcry3_d3d11.exe"]

MARKERS = ["StartArguments", "ExecutableName", "InstallDir", "installdir", "execPath",
           "GameUpdate", "StartResult", "GameStarter", "Installs", "Launcher",
           "Software\\Ubisoft", "Ubisoft Game Launcher", "Far Cry 3", "FarCry3",
           "SKU", "Version", "Language"]

# call sites reported by scripts/fc3_iat_scan.py (FC3_d3d11.dll)
IAT_SITES = {
    "RegOpenKeyExA": [0x10c51387, 0x1176e306, 0x1176e3e1],
    "RegQueryValueExA": [0x10c513ae, 0x1176e33d, 0x11ad0c45],
}

PUSH = re.compile(rb"\x68(....)", re.S)


def hits_for(pe, marker):
    out = []
    for kind, blob in (("ascii", marker.encode("ascii")), ("utf16", marker.encode("utf-16-le"))):
        i = pe.d.find(blob)
        while i >= 0:
            out.append((pe.off2va(i), kind, i))
            i = pe.d.find(blob, i + 1)
            if len(out) > 30:
                break
    return out


def func_start(pe, va, max_back=0x2000):
    tva, tend, tptr, tsize = pe.text
    off = pe.va2off(va)
    for back in range(1, max_back):
        c = off - back
        if c <= tptr:
            break
        if pe.d[c - 1] in (0xC3, 0xCC) and pe.d[c:c + 3] == b"\x55\x8B\xEC":
            return tva + (c - tptr)
    return None


def dump_func(pe, fs, span=0x1600):
    off = pe.va2off(fs)
    body = pe.d[off:off + span]
    out = []
    for m in PUSH.finditer(body):
        v = struct.unpack("<I", m.group(1))[0]
        o = pe.va2off(v)
        if o is None:
            continue
        raw = pe.d[o:o + 96].split(b"\x00")[0]
        if len(raw) >= 3 and all(32 <= c < 127 for c in raw):
            out.append((fs + m.start(), v, raw.decode("ascii", "replace")))
    return out


def main():
    for path in (sys.argv[1:] or DEFAULT):
        try:
            pe = PE(path)
        except Exception as exc:
            print("%s: cannot open (%s)" % (path, exc))
            continue
        print("\n=== %s base=0x%x" % (path, pe.base))
        for m in MARKERS:
            h = hits_for(pe, m)
            if h:
                print("  %-22s %s" % (m, ", ".join("%s@%s" % (k, ("0x%x" % v) if v else "raw0x%x" % o) for v, k, o in h[:10])))
        if pe.base < 0x10000000:
            continue
        print("  --- registry call sites ---")
        seen = set()
        for name, sites in IAT_SITES.items():
            for s in sites:
                fs = func_start(pe, s)
                tag = "%s site 0x%x func %s" % (name, s, ("0x%x" % fs) if fs else "?")
                print("   " + tag)
                if fs and fs not in seen:
                    seen.add(fs)
                    for ref, v, txt in dump_func(pe, fs)[:30]:
                        print("      0x%x imm 0x%x %r" % (ref, v, txt[:80]))
                else:
                    seen.add(fs)


if __name__ == "__main__":
    main()
