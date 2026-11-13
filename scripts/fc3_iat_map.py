"""Map IAT slots for chosen imported functions and list the code sites that use them (read-only).

Usage: python -I scripts/fc3_iat_map.py <pe file> [out.tsv]
Prints, per function of interest: the IAT slot VA, every 'call [slot]' / 'mov reg,[slot]' site,
the 16 bytes before each site (so the surrounding instruction pattern can be read), and the
function prologue start found by walking back to '55 8b ec' (push ebp / mov ebp,esp).

Section mapping uses max(virtual_size, raw_size) so entries living in a section whose raw size
is smaller than its virtual size are still resolved.
"""
import struct
import sys

INTEREST = [
    "OpenMutexA", "CreateMutexA", "OpenEventA", "CreateEventA", "OpenFileMappingA",
    "ShellExecuteA", "ShellExecuteW", "ShellExecuteExA", "ShellExecuteExW",
    "CreateProcessA", "CreateProcessW", "GetCommandLineA", "GetCommandLineW",
    "GetModuleFileNameA", "FindWindowA", "LoadLibraryA", "GetProcAddress",
]


def parse(path):
    d = open(path, "rb").read()
    pe = struct.unpack_from("<I", d, 0x3C)[0]
    opt = struct.unpack_from("<H", d, pe + 20)[0]
    base = struct.unpack_from("<I", d, pe + 24 + 28)[0]
    nsec = struct.unpack_from("<H", d, pe + 6)[0]
    so = pe + 24 + opt
    secs = []
    for i in range(nsec):
        nm = d[so + i * 40: so + i * 40 + 8].rstrip(b"\0").decode(errors="replace")
        vs, va, rs, rp = struct.unpack_from("<IIII", d, so + i * 40 + 8)
        secs.append((nm, base + va, max(vs, rs), rs, rp))

    def va2off(va):
        for nm, sva, span, rs, rp in secs:
            if sva <= va < sva + span:
                if va - sva < rs:
                    return rp + (va - sva)
                return None
        return None

    def off2va(off):
        for nm, sva, span, rs, rp in secs:
            if rp <= off < rp + rs:
                return sva + off - rp
        return None

    text = next((s for s in secs if s[0] == ".text"), secs[0])
    imp_dd = 96 if opt == 224 else 112
    imp_rva = struct.unpack_from("<I", d, pe + 24 + imp_dd + 8)[0]

    slots = {}
    o = va2off(base + imp_rva)
    while o is not None and d[o:o + 4] != b"\0\0\0\0":
        name_rva, tl = struct.unpack_from("<II", d, o)
        if tl == 0:
            tl = name_rva
        k = va2off(base + tl)
        while k is not None:
            entry = struct.unpack_from("<I", d, k)[0]
            if entry == 0:
                break
            if entry & 0x80000000:
                k += 4
                continue
            nm_off = va2off(base + (entry & 0x7FFFFFFF) + 2)
            nm = d[nm_off:d.find(b"\0", nm_off)].decode("latin1") if nm_off else "?"
            slot_va = base + tl + (k - va2off(base + tl))
            dll_off = va2off(base + name_rva)
            dll = d[dll_off:d.find(b"\0", dll_off)].decode("latin1") if dll_off else "?"
            slots[nm] = (slot_va, dll)
            k += 4
        o += 20

    tva, tspan, trs, trp = text[1], text[2], text[3], text[4]
    rows = []
    for nm in INTEREST:
        if nm not in slots:
            continue
        slot, dll = slots[nm]
        needle = struct.pack("<I", slot)
        blob = d[trp:trp + trs]
        i = blob.find(needle)
        while i >= 0:
            prev = blob[i - 1] if i >= 1 else 0
            kind = "call [slot]" if prev == 0x15 else ("mov reg,[slot]" if prev == 0x05 or 0xB8 <= prev <= 0xBF else "")
            if kind:
                site = off2va(trp + i - (2 if kind.startswith("call") else 1))
                ctx_off = trp + i - 16
                ctx = d[ctx_off:ctx_off + 20].hex(" ")
                pro = prologue(d, ctx_off)
                rows.append((nm, dll, "%08x" % slot, "%08x" % (site or 0), kind, ctx,
                             "%08x" % pro if pro else ""))
            i = blob.find(needle, i + 1)
    return rows


def prologue(d, off, window=512):
    """Walk back from a code offset to the enclosing function prologue (55 8b ec)."""
    for k in range(off, max(0, off - window), -1):
        if d[k] == 0x55 and d[k + 1] == 0x8B and d[k + 2] == 0xEC:
            head = d[k + 3:k + 24]
            if b"\xcc" not in head[:4] or True:
                return k
    return None


def main():
    path = sys.argv[1]
    out = sys.argv[2] if len(sys.argv) > 2 else None
    rows = parse(path)
    print("%s  (%d sites)" % (path, len(rows)))
    for r in rows:
        print("%-18s %-14s slot=%s site=%s %-16s pro=%s\n    ctx=%s" %
              (r[0], r[1], r[2], r[3], r[4], r[6], r[5]))
    if out:
        with open(out, "w", encoding="utf-8", newline="\n") as f:
            f.write("function\tdll\tslot_va\tsite_va\tkind\tprologue_va\tcontext\n")
            for r in rows:
                f.write("\t".join(r) + "\n")


if __name__ == "__main__":
    main()
