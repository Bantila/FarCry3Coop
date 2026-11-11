"""Map the quick-launch command-line handling in a FC3.dll build (1.06 Uplay build here).

Uses fc3_addrmap.py's PE parser (plain byte scanning, no Ghidra). Reports:
  1. every '-switch' string in the launcher command-line table and the code that references it,
  2. the nearest 'push imm32' callback before each reference (the registration pattern),
  3. imports of OpenMutexA / CreateProcessA / ShellExecute* and the code sites that call them.

Usage: python -I fc3_quicklaunch_map.py <FC3.dll> [out.tsv]
"""
import os
import struct
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fc3_addrmap import PE  # noqa: E402

# switches documented by the prior-art notes (1.05 FUN_10652061 command-line checker)
SWITCHES = [
    "-host", "-client", "-coop", "-login", "-ip", "-online", "-offline", "-wait",
    "-quickmatch", "-dedicated", "-sessionuid", "-bfname", "-deathmatch", "-domination",
    "-headquarters", "-firestorm", "-dash", "-class", "-spawn", "-spawnpos", "-spawnangle",
    "-netemulator", "-ranked", "-mapsource", "-Dx9", "-dx11", "-log", "-profile",
]
# functions whose import thunk we want call sites for
IMPORTS_OF_INTEREST = ["OpenMutexA", "CreateMutexA", "CreateProcessA", "CreateProcessW",
                       "ShellExecuteA", "ShellExecuteW", "ShellExecuteExA", "ShellExecuteExW",
                       "GetCommandLineA", "GetCommandLineW"]


def import_thunks(pe):
    """VA of each import thunk (IAT slot) by name, from the import directory."""
    d = pe.d
    nt = struct.unpack_from("<I", d, 0x3C)[0]
    opt = nt + 24
    size_opt = struct.unpack_from("<H", d, nt + 20)[0]
    dirs_off = opt + 96  # PE32 data directories start at optional-header offset 96
    imp_rva, imp_size = struct.unpack_from("<II", d, dirs_off + 8 * 1)
    sec = list(pe.sec.values())  # (va, raw_ptr, raw_size) per section

    def off2va(o):
        for va, ptr, size in sec:
            if ptr <= o < ptr + size:
                return va + o - ptr
        return None

    def va2off(v):
        for va, ptr, size in sec:
            if va <= v < va + size:
                return ptr + v - va
        return None

    out = {}
    o = va2off(pe.base + imp_rva)
    while o is not None and d[o:o + 4] != b"\0\0\0\0":
        name_rva, tl = struct.unpack_from("<II", d, o)
        lookup = va2off(pe.base + (tl if tl else name_rva))
        if lookup is None:
            break
        k = lookup
        while True:
            entry = struct.unpack_from("<I", d, k)[0]
            if entry == 0:
                break
            if entry & 0x80000000:
                k += 4
                continue
            so = va2off(pe.base + (entry & 0x7FFFFFFF) + 2)
            if so is None:
                k += 4
                continue
            nm = d[so:d.find(b"\0", so)].decode("latin1")
            slot_va = pe.base + tl + (k - lookup) if tl else pe.base + name_rva + (k - lookup)
            out.setdefault(nm, slot_va)
            k += 4
        o += 20
    return out


def call_sites(pe, slot_va):
    """Offsets of 'call [slot]' (FF 15 <imm32>) and 'mov r32,[slot]' (A1/8B /r) using slot_va."""
    tva, tend, tptr, tsize = pe.text
    text = pe.d[tptr:tptr + tsize]
    needle = struct.pack("<I", slot_va)
    hits = []
    i = text.find(needle)
    while i >= 0:
        prev = text[i - 1] if i >= 1 else 0
        if prev == 0x15:                      # FF 15 -> call [addr]
            hits.append(("call", tptr + i - 2))
        elif prev == 0x05 or 0xB8 <= prev <= 0xBF:   # mov reg,[addr]
            hits.append(("mov", tptr + i - 1))
        i = text.find(needle, i + 1)
    return hits


def nearest_push(pe, off, window=64):
    for k in range(off - 5, off - window, -1):
        if pe.d[k] == 0x68:
            v = struct.unpack_from("<I", pe.d, k + 1)[0]
            if pe.in_text(v):
                return v
    return None


def main():
    dll = sys.argv[1]
    out = sys.argv[2] if len(sys.argv) > 2 else None
    pe = PE(dll)
    print("%s base 0x%08x text 0x%08x-0x%08x" % (dll, pe.base, pe.text[0], pe.text[1]))

    rows = []
    for sw in SWITCHES:
        for sva in pe.find_cstring(sw):
            for r in pe.code_refs(sva):
                rows.append(("switch " + sw, "0x%08x" % sva, "0x%08x" % pe.off2va(r),
                             "0x%08x" % nearest_push(pe, r) if nearest_push(pe, r) else ""))
    thunks = import_thunks(pe)
    for nm in IMPORTS_OF_INTEREST:
        slot = thunks.get(nm)
        if not slot:
            rows.append((nm, "", "NOT IMPORTED", ""))
            continue
        for kind, off in call_sites(pe, slot):
            rows.append(("%s (%s)" % (nm, kind), "0x%08x" % slot, "0x%08x" % pe.off2va(off), ""))
    for r in rows:
        print("\t".join(r))
    if out:
        with open(out, "w", encoding="utf-8", newline="\n") as f:
            f.write("what\tstring_or_slot_va\tcode_va\tnearest_push\n")
            for r in rows:
                f.write("\t".join(r) + "\n")


if __name__ == "__main__":
    main()
