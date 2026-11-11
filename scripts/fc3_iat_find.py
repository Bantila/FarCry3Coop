"""fc3_iat_find.py — find IAT slots by imported NAME, then list .text sites that call them.

Read-only. Usage: python -I scripts/fc3_iat_find.py <pe file> <name> [name2 ...]
Name matching is case-insensitive substring. Prints the DLL+function for each matching slot, the
slot VA, and every .text occurrence of `ff 15 <slot>` / `ff d?`-style access (`ff 35`,`8b 1d`,`8b 05`,
`c7 05`) plus plain `call [slot]`. Bytes only — no disassembly needed, so this is fast and robust
against misaligned function starts (the mistake that hid these sites before).
"""
import struct
import sys

sys.path.insert(0, r"D:/Projects/Co-op Anything/FarCry3Coop-bantila/scripts")
from fc3_addrmap import PE  # noqa: E402


def build_iat(pe):
    """Return {slot_va: "Dll!func"} for a 32-bit PE."""
    d = pe.d
    peoff = struct.unpack_from("<I", d, 0x3C)[0]
    sizeopt = struct.unpack_from("<H", d, peoff + 20)[0]
    dd = peoff + 24 + sizeopt
    imp_rva, imp_size = struct.unpack_from("<II", d, dd + 8)
    off = pe.va2off(pe.base + imp_rva)
    out = {}
    i = 0
    while True:
        orig, name_rva, ts, fwd, orig_thk = struct.unpack_from("<IIIII", d, off + i * 20)
        if name_rva == 0:
            break
        dll_off = pe.va2off(pe.base + name_rva)
        dll = d[dll_off:dll_off + 64].split(b"\0")[0].decode("ascii", "replace")
        ilt_rva = orig or orig_thk
        il_off = pe.va2off(pe.base + ilt_rva)
        k = 0
        while True:
            entry = struct.unpack_from("<I", d, il_off + k * 4)[0]
            if entry == 0:
                break
            if entry & 0x80000000:
                k += 1
                continue
            nm_off = pe.va2off(pe.base + (entry & 0x7FFFFFFF)) + 2
            name = d[nm_off:nm_off + 128].split(b"\0")[0].decode("ascii", "replace")
            out[pe.base + ilt_rva + k * 4] = "%s!%s" % (dll, name)
            k += 1
        i += 1
    return out


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        return 2
    path = sys.argv[1]
    names = [n.lower() for n in sys.argv[2:]]
    pe = PE(path)
    iat = build_iat(pe)
    hits = {va: lbl for va, lbl in iat.items() if any(n in lbl.lower() for n in names)}
    if not hits:
        print("no imported name matches %s" % names)
        return 1
    for va, lbl in sorted(hits.items()):
        print("IAT slot 0x%08x = %s" % (va, lbl))
    for va, lbl in sorted(hits.items()):
        pat = struct.pack("<I", va)
        tva, tend, tptr, tsize = pe.text
        blob = pe.d[tptr:tptr + tsize]
        sites = []
        pos = 0
        while True:
            i = blob.find(pat, pos)
            if i < 0:
                break
            sites.append(tva + i)
            pos = i + 4
        print("\n%s: %d .text reference(s)" % (lbl, len(sites)))
        for cv in sites[:40]:
            print("  site 0x%08x" % cv)
        if len(sites) > 40:
            print("  ... %d more" % (len(sites) - 40))
    return 0


if __name__ == "__main__":
    sys.exit(main())
