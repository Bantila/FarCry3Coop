"""Locate the 1.06 re-exec bootstrap inside FC3_d3d11.dll (read-only).

Scans the string neighbourhood around `SOFTWARE\\Ubisoft`, `-language` and `Far Cry 3`,
resolves code references to those strings, and dumps the surrounding raw bytes so the
bootstrap function and its call sites can be identified without a disassembler.

Usage: python -I scripts/fc3_reexec_probe.py [dll ...]
Default target: H:/FarCryCoop/TestFC3/bin/FC3_d3d11.dll
"""
import re
import struct
import sys

sys.path.insert(0, r"D:/Projects/Co-op Anything/FarCry3Coop-bantila/scripts")
from fc3_addrmap import PE  # noqa: E402

ANCHORS = [b"SOFTWARE\\Ubisoft", b"-language", b"Far Cry 3", b"upc_r1_loader", b"ShellExecuteA"]


def ascii_run(data, start, back=96, fwd=256):
    """Print the printable run that contains offset `start`."""
    a = start
    while a > 0 and 0x20 <= data[a - 1] < 0x7F:
        a -= 1
    b = start
    n = len(data)
    while b < n and 0x20 <= data[b] < 0x7F:
        b += 1
    return a, data[a:b].decode(errors="replace")


def run(dll):
    pe = PE(dll)
    print("== %s" % dll)
    for anchor in ANCHORS:
        i = pe.d.find(anchor)
        hits = 0
        while i >= 0 and hits < 6:
            va = pe.off2va(i)
            a0, s = ascii_run(pe.d, i)
            print("  anchor %-18s raw=0x%08x va=%s run(raw 0x%08x)=%r" % (
                anchor.decode(errors="replace"), i, ("0x%08x" % va) if va else "?",
                a0, s[:160]))
            if va:
                refs = pe.code_refs(va)
                print("     code refs (%d): %s" % (len(refs), ", ".join("0x%08x" % pe.off2va(r) for r in refs[:8])))
                for r in refs[:4]:
                    f = function_start(pe, r)
                    fva = pe.off2va(f)
                    print("     function containing ref 0x%08x -> 0x%08x" % (pe.off2va(r), fva))
                    print("       prologue: " + " ".join("%02X" % b for b in pe.d[f:f + 40]))
            hits += 1
            i = pe.d.find(anchor, i + 1)
        print()


def function_start(pe, off):
    k = off
    while k > 16:
        if pe.d[k:k + 3] == b"\x55\x8b\xec" and (pe.d[k - 1] in (0xCC, 0xC3, 0x90) or pe.d[k - 3] == 0xC2):
            return k
        k -= 1
    raise ValueError("function start not found")


if __name__ == "__main__":
    for p in sys.argv[1:] or [r"H:/FarCryCoop/TestFC3/bin/FC3_d3d11.dll"]:
        run(p)
