"""Far Cry 3 quick-launch string context dump (read-only).

Prints readable context around hits of selected markers.

Usage: python -X utf8 scripts/fc3_args_context.py [--max 12]
"""

import re
import struct
import sys

FILES = [
    r"H:/FarCryCoop/TestFC3/bin/FC3Updater.exe",
    r"H:/FarCryCoop/TestFC3/bin/upc_r1_loader.dll",
    r"H:/FarCryCoop/TestFC3/bin/FC3_d3d11.dll",
]

MARKERS = ["QuickLaunch", "quicklaunch", "StartArguments", "arguments", "Arguments", "InstallDir", "Software\\Ubisoft", "upc_r1_loader"]

WINDOW = 220


def pe_info(data):
    if data[:2] != b"MZ":
        return None
    e_lfanew = struct.unpack_from("<I", data, 0x3C)[0]
    machine, nsec = struct.unpack_from("<HH", data, e_lfanew + 4)
    opt_size = struct.unpack_from("<H", data, e_lfanew + 16)[0]
    magic = struct.unpack_from("<H", data, e_lfanew + 24)[0]
    if magic == 0x20B:
        image_base = struct.unpack_from("<Q", data, e_lfanew + 24 + 28)[0]
    else:
        image_base = struct.unpack_from("<I", data, e_lfanew + 24 + 28)[0]
    sec_off = e_lfanew + 24 + opt_size
    secs = []
    for i in range(nsec):
        o = sec_off + i * 40
        name = data[o : o + 8].rstrip(b"\x00").decode("latin1")
        vsize, vaddr, rsize, raddr = struct.unpack_from("<IIII", data, o + 8)
        secs.append((name, vaddr, vsize, raddr, rsize))
    return {"base": image_base, "secs": secs}


def rva_of(info, off):
    for _n, vaddr, _vs, raddr, rsize in info["secs"]:
        if raddr <= off < raddr + max(rsize, 1):
            return vaddr + (off - raddr)
    return None


def printable_span(data, lo, hi):
    """Return the printable ASCII and UTF-16 runs touching the window."""
    chunk = data[lo:hi]
    ascii_runs = re.findall(rb"[\x20-\x7e]{3,}", chunk)
    u16_runs = []
    i = 0
    while i < len(chunk) - 3:
        if chunk[i + 1] == 0 and 0x20 <= chunk[i] <= 0x7E:
            j = i
            s = []
            while j + 1 < len(chunk) and chunk[j + 1] == 0 and 0x20 <= chunk[j] <= 0x7E:
                s.append(chr(chunk[j]))
                j += 2
            if len(s) >= 3:
                u16_runs.append("".join(s))
            i = j
        else:
            i += 1
    return ascii_runs, u16_runs


def main():
    max_hits = 12
    files = FILES
    for i, a in enumerate(sys.argv):
        if a == "--max":
            max_hits = int(sys.argv[i + 1])
        if a == "--file":
            files = sys.argv[i + 1].split(",")
        if a == "--markers":
            MARKERS_LOCAL = sys.argv[i + 1].split(",")
    for path in files:
        data = open(path, "rb").read()
        info = pe_info(data)
        print("=" * 70)
        print(path, "base=%s" % hex(info["base"]))
        for m in MARKERS:
            for enc, needle in (("a", m.encode("ascii")), ("u16", m.encode("utf-16le"))):
                start = 0
                n = 0
                while n < max_hits:
                    off = data.find(needle, start)
                    if off < 0:
                        break
                    start = off + 1
                    n += 1
                    rva = rva_of(info, off)
                    va = info["base"] + rva if rva is not None else None
                    lo = max(0, off - WINDOW)
                    hi = min(len(data), off + len(needle) + WINDOW)
                    a_runs, u_runs = printable_span(data, lo, hi)
                    print("-- %s %s off=0x%x va=%s" % (m, enc, off, hex(va) if va else "-"))
                    for r in a_runs:
                        print("     a: %s" % r.decode("latin1")[:120])
                    for r in u_runs:
                        print("     u: %s" % r[:120])


if __name__ == "__main__":
    main()
