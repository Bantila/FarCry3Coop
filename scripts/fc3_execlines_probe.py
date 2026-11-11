"""Find the execLines consumer in the 1.06 binaries (read-only).

For each target string VA (default: the `execLines` session field name 0x11f90af0 and the
1.06 launcher's exec-line write sites) print every `push imm32` / `mov r32, imm32` reference
in .text, then disassemble +/- 0x40 bytes around each reference with the fc3_dis annotator.

Usage: python -I games/far-cry-3/tools/fc3_execlines_probe.py <pe file> [target va hex ...]
"""
import sys

sys.path.insert(0, r"D:/Projects/Co-op Anything/FarCry3Coop-bantila/scripts")
sys.path.insert(0, r"D:/Projects/Co-op Anything/FarCryCoop/tools")

from fc3_addrmap import PE  # noqa: E402
import fc3_dis  # noqa: E402

DEFAULT = ["0x11f90af0"]


def main(path, targets):
    pe = PE(path)
    print("== %s  base 0x%08x" % (path, pe.base))
    for va in targets:
        refs = pe.code_refs(va)
        print("\n-- target 0x%08x : %d code refs" % (va, len(refs)))
        for off in refs[:24]:
            rva = pe.off2va(off)
            print("  ref @ 0x%08x" % rva)
            fc3_dis.main(path, rva - 0x40, rva + 0x60, 40)


if __name__ == "__main__":
    a = sys.argv[1:]
    path = a[0]
    tg = [int(x, 16) for x in (a[1:] or DEFAULT)]
    main(path, tg)
