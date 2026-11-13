"""Far Cry 3 launch-arg marker scan (read-only).

For each file, find ASCII and UTF-16LE occurrences of the given markers,
compute the VA (image base + raw rva), and dump 32 bytes around each hit.

Usage: python -X utf8 scripts/fc3_args_scan.py [--dir DIR] [--markers a,b,c]
"""

import argparse
import struct
import sys

MARKERS = [
    "StartArguments",
    "ExecutableName",
    "InstallDir",
    "arguments",
    "Arguments",
    "-upc_",
    "QuickLaunch",
    "quicklaunch",
    "extraCommand",
    "CommandLine",
    "command line",
    "upc_r1_loader",
    "Software\\Ubisoft",
    "Far Cry 3",
    "LaunchOptions",
    "AdditionalArguments",
]

DIRS = [
    r"H:/FarCryCoop/TestFC3/bin",
    r"C:/Program Files (x86)/Ubisoft/Ubisoft Game Launcher",
]


def pe_info(data):
    if data[:2] != b"MZ":
        return None
    e_lfanew = struct.unpack_from("<I", data, 0x3C)[0]
    if data[e_lfanew : e_lfanew + 4] != b"PE\x00\x00":
        return None
    machine, nsec = struct.unpack_from("<HH", data, e_lfanew + 4)
    opt_size = struct.unpack_from("<H", data, e_lfanew + 16)[0]
    magic = struct.unpack_from("<H", data, e_lfanew + 24)[0]
    image_base = struct.unpack_from("<Q", data, e_lfanew + 24 + 28)[0] if magic == 0x20B else struct.unpack_from("<I", data, e_lfanew + 24 + 28)[0]
    sec_off = e_lfanew + 24 + opt_size
    secs = []
    for i in range(nsec):
        o = sec_off + i * 40
        name = data[o : o + 8].rstrip(b"\x00").decode("latin1")
        vsize, vaddr, rsize, raddr = struct.unpack_from("<IIII", data, o + 8)
        secs.append((name, vaddr, vsize, raddr, rsize))
    return {"base": image_base, "secs": secs}


def rva_of(secs, off):
    for _name, vaddr, _vsize, raddr, rsize in secs:
        if raddr <= off < raddr + max(rsize, 1):
            return vaddr + (off - raddr)
    return None


def find_all(data, needle):
    out = []
    start = 0
    while True:
        i = data.find(needle, start)
        if i < 0:
            return out
        out.append(i)
        start = i + 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", action="append")
    ap.add_argument("--markers")
    ap.add_argument("--max-hits", type=int, default=6)
    args = ap.parse_args()
    dirs = args.dir or DIRS
    markers = args.markers.split(",") if args.markers else MARKERS

    for d in dirs:
        try:
            names = sorted(__import__("os").listdir(d))
        except OSError as exc:
            print("== %s MISSING (%s)" % (d, exc))
            continue
        for name in names:
            if not name.lower().endswith((".exe", ".dll")):
                continue
            path = d + "/" + name
            try:
                data = open(path, "rb").read()
            except OSError as exc:
                print("  skip %s: %s" % (path, exc))
                continue
            info = pe_info(data)
            print("== %s  size=%d base=%s" % (path, len(data), hex(info["base"]) if info else "-"))
            hits_total = 0
            for m in markers:
                for enc, needle in (("a", m.encode("ascii")), ("u16", m.encode("utf-16le"))):
                    hits = find_all(data, needle)
                    if not hits:
                        continue
                    hits_total += len(hits)
                    print("   %-18s %s count=%d" % (m, enc, len(hits)))
                    for off in hits[: args.max_hits]:
                        rva = rva_of(info["secs"], off) if info else None
                        va = (info["base"] + rva) if (info and rva is not None) else None
                        ctx = data[max(0, off - 8) : off + len(needle) + 24]
                        print("      off=0x%x rva=%s va=%s ctx=%s" % (off, hex(rva) if rva is not None else "-", hex(va) if va is not None else "-", ctx.hex()))
            if hits_total == 0:
                print("   (no marker hits)")


if __name__ == "__main__":
    main()
