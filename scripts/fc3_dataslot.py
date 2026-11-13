"""Which data slot is which: classify absolute data addresses seen in FC3*.dll code.

Answers two open questions at once:
  - FC3_d3d11.dll 0x11fdee10   (target of `call dword ptr [0x11fdee10]` at 0x11aa301a)
  - FC3.dll session-object vftable slot 0x74 (0x11341dc0 path: mov ecx,[eax]; mov eax,[ecx]; call [eax+0x74])

Usage: python -I fc3_dataslot.py <pe-file> <VA> [<VA> ...]
"""
import struct, sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

SECTION_TRIPLES = {  # hardcoded (PE header parsing is fragile on these files)
    "FC3_d3d11.dll": {"text": (0x10001000, 0x400, 0x1BDF200),
                      "rdata": (0x11BE1000, 0x1BDF600, 0x4C7E00),
                      "data": (0x2094000, 0x2092000, 0xE7C00)},
    "FC3.dll": {"text": (0x10001000, 0x400, 0x1BC9E00),
                "rdata": (0x11BC1000, 0x1BCA200, 0x4C7E00),
                "data": (0x2088000, 0x2087000, 0xE7C00)},
}


def load(pe_path, triples):
    d = open(pe_path, "rb").read()
    name = pe_path.replace("\\", "/").split("/")[-1]
    sec = triples.get(name, triples)
    out = {}
    for k, (va, raw, size) in sec.items():
        out[k] = (va, va + size, raw)
    return d, out


def sec_of(sections, va):
    for k, (start, end, raw) in sections.items():
        if start <= va < end:
            return k, va - start + raw
    return None, None


def main():
    pe_path = sys.argv[1]
    va_list = [int(a, 16) for a in sys.argv[2:]]
    key = pe_path.replace("\\", "/").split("/")[-1]
    triples = SECTION_TRIPLES.get(key)
    if triples is None:
        print("no section triples for", key, "- edit SECTION_TRIPLES")
        return
    d, sections = load(pe_path, triples)
    print("file", pe_path, "size", len(d), "sections",
          {k: (hex(v[0]), hex(v[1])) for k, v in sections.items()})
    for va in va_list:
        sec, off = sec_of(sections, va)
        if sec is None:
            print(hex(va), "-> not mapped in file (bss?)")
            continue
        row = d[off:off + 32]
        ptrs = [struct.unpack_from("<I", d, off + 4 * i)[0] for i in range(8)]
        named = []
        for p in ptrs:
            s, _ = sec_of(sections, p)
            named.append("%s:%s" % (s, hex(p)) if s else hex(p))
        print("%#010x in %s off=%#x bytes=%s" % (va, sec, off, row.hex()))
        print("   first 8 LE32 values:", " ".join(named))
        # printable ASCII nearby
        txt = d[off:off + 64]
        printable = "".join(bytes([c]).decode("ascii", "replace") if 32 <= c < 127 else "." for c in txt)
        print("   as text:", printable)


if __name__ == "__main__":
    main()
