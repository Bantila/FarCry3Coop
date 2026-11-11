#!/usr/bin/env python3
"""
fc3_reloc_xref.py — cross-reference an absolute global VA in FC3.dll / FC3_d3d11.dll.

PREMISE CORRECTED (2026-11-03, was wrong before this date): the old version claimed that a
`cmp eax, [0x12829424]` does not contain the literal bytes of the target VA in the file, so that
the only route was walking .reloc. That is wrong for these images: disp32 fields inside .text hold
the *default* image-base-relative VA verbatim, so the accesses are found by a little-endian byte
scan of the disp32 field, exactly like the 17 502 hits recorded for 0x12829424 in NOTES.md.
Walking .reloc instead yields relocation *patch sites* (storage that the loader rebases), never the
code accesses, which is why every lookup used to return 0.

What the scan actually covers:
  * ModRM disp32 memory forms: 8b /r (mod=00 rm=100) -> 05 0d 15 25 35 ... 3d, plus 89 store,
    8d lea, 81/83 group, c6/c7 immediate-to-memory, ff /6 push, ff /7 jmp, ff /2 /6 call/jmp,
    0f b6/b7/be/bf zero- and sign-extend loads, with optional 66 / f2 / f3 prefixes.
  * each byte hit is *verified by backward decoding*: the script tries every candidate instruction
    start up to 15 bytes back, disassembles forward with capstone and accepts only an instruction
    that ends exactly at the disp32 field and whose operand names the target address. This removes
    false positives coming from data that coincidentally looks like the VA.
  * pointer tables: every writable section is scanned for the packed VA used as a stored pointer.
  * relocation patch sites are reported separately (--mode reloc) as loader evidence, not as xrefs.
    Each site is reported with the value stored there *before* the loader patches it, which for an
    image left at its default image base is the absolute VA that the slot points at. That is what
    makes --mode reloc worth asking: "which table stores a pointer to this VA?"
    (The previous version returned the field VA twice as the target, so every query matched its own
    own patch site and the answer was always a false positive; the type names came from the ARM64
    table, so a 32-bit HIGHLOW entry was printed as HIGH_ABS.)

Read-only: the target PE is opened for reading, nothing is written, and no game file is modified.

Usage:
  python scripts/fc3_reloc_xref.py <pe path> <VA> [VA ...] [--mode code|reloc|both]
                                     [--max-print N] [--verify-limit N] [--window N]
"""
import sys, struct, argparse

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

try:
    import capstone
except Exception:
    print("capstone missing: python -m pip install capstone"); sys.exit(1)

RELOC_TYPES = {0: "ABSOLUTE(padding)", 1: "HIGH", 2: "LOW", 3: "HIGHLOW", 4: "HIGHADJ",
               5: "MIPS_JMPADDR", 10: "DIR64"}
IMAGE_FILE_MACHINE_NAMES = {0x14C: "x86 (32-bit)", 0x8664: "x86_64"}


class PE:
    """Minimal self-contained PE reader: sections, VA<->offset mapping, executable sections."""

    def __init__(self, path):
        self.path = path
        self.d = open(path, "rb").read()
        e = struct.unpack_from("<I", self.d, 0x3C)[0]
        self.nsec = struct.unpack_from("<H", self.d, e + 6)[0]
        sizeofopt = struct.unpack_from("<H", self.d, e + 20)[0]
        self.machine = struct.unpack_from("<H", self.d, e + 4)[0]
        self.base = struct.unpack_from("<I", self.d, e + 24 + 28)[0]
        self.sizeofimage = struct.unpack_from("<I", self.d, e + 24 + 56)[0]
        self.entry = struct.unpack_from("<I", self.d, e + 24 + 16)[0]
        self.image_type = struct.unpack_from("<H", self.d, e + 24 + 6)[0]
        sectab = e + 24 + sizeofopt
        self.sec = {}
        self.order = []
        for i in range(self.nsec):
            o = sectab + i * 40
            nm = self.d[o:o + 8].rstrip(b"\0").decode("latin-1")
            vsz, va, rawsz, ptr = struct.unpack_from("<IIII", self.d, o + 8)
            chars = struct.unpack_from("<I", self.d, o + 36)[0]
            self.sec[nm] = (self.base + va, vsz, ptr, rawsz, chars)
            self.order.append(nm)

    def va2off(self, va):
        for nm in self.order:
            sv, vsz, ptr, rawsz, _ = self.sec[nm]
            if sv <= va < sv + max(vsz, rawsz):
                off = ptr + (va - sv)
                # `off` is an absolute file offset, so it must be bounded by ptr + rawsz
                # (rawsz alone is only the section length and rejects every section after
                # the first one).
                return off if ptr <= off < ptr + rawsz and off < len(self.d) else None
        return None

    def off2va(self, off):
        for nm in self.order:
            sv, vsz, ptr, rawsz, _ = self.sec[nm]
            if ptr <= off < ptr + rawsz:
                return sv + (off - ptr)
        return None

    def sections(self, executable=False, writable=False):
        out = []
        for nm in self.order:
            sv, vsz, ptr, rawsz, chars = self.sec[nm]
            if executable and not (chars & 0x20000000):   # IMAGE_SCN_MEM_EXECUTE
                continue
            if writable and not (chars & 0x80000000):     # IMAGE_SCN_MEM_WRITE
                continue
            out.append((nm, sv, vsz, ptr, rawsz, chars))
        return out

    def cstr(self, va, maxlen=96):
        off = self.va2off(va)
        if off is None:
            return None
        raw = self.d[off:off + maxlen].split(b"\0", 1)[0]
        if 0 < len(raw) and all(0x20 <= b < 0x7F for b in raw):
            return raw.decode("latin-1")
        return None

    def reloc_entries(self):
        """(patch-site VA, value stored there at load time, type name) for every real relocation
        entry in the image. Type 0 (ABSOLUTE) is padding and is skipped. The stored value is read
        from the site itself: for an image at its default image base it is the target VA."""
        out = []
        for nm in self.order:
            if nm != ".reloc":
                continue
            sv, vsz, ptr, rawsz, _ = self.sec[nm]
            blob = self.d[ptr:ptr + rawsz]
            pos = 0
            while pos + 8 <= len(blob):
                page_rva, block_size = struct.unpack_from("<II", blob, pos)
                if block_size < 8 or block_size > len(blob) - pos:
                    break
                for i in range((block_size - 8) // 2):
                    ent = struct.unpack_from("<H", blob, pos + 8 + i * 2)[0]
                    typ = ent >> 12
                    off = ent & 0xFFF
                    if typ == 0:
                        continue                                    # padding, nothing patched
                    site_va = self.base + page_rva + off
                    site = self.va2off(site_va)
                    stored = None
                    if site is not None:
                        if typ == 10 and site + 8 <= len(self.d):   # DIR64
                            stored = struct.unpack_from("<Q", self.d, site)[0]
                        elif site + 4 <= len(self.d):               # HIGH/LOW/HIGHLOW/HIGHADJ
                            stored = struct.unpack_from("<I", self.d, site)[0]
                    out.append((site_va, stored, RELOC_TYPES.get(typ, "type%d" % typ)))
                pos += block_size
        return out


DISASSEMBLERS = {}


def cs_for(machine):
    """capstone Cs object for this machine (FC3 is 32-bit x86 despite the PE64 header name)."""
    key = machine
    if key not in DISASSEMBLERS:
        mode = capstone.CS_MODE_32 if machine == 0x14C else capstone.CS_MODE_64
        md = capstone.Cs(capstone.CS_ARCH_X86, mode)
        md.detail = False
        DISASSEMBLERS[key] = md
    return DISASSEMBLERS[key]


def verify_site(pe, disp_va, target, window=15):
    """Return the disassembled instruction that carries the disp32 field at disp_va, or None.

    Tries every candidate instruction start from disp_va-window .. disp_va-1 and accepts the first
    decoded instruction whose end address equals disp_va and whose operands name the target.
    """
    md = cs_for(pe.machine)
    off = pe.va2off(disp_va)
    if off is None:
        return None
    want = "0x%x" % target
    lo = max(off - window, 0)
    for start in range(off - 1, lo - 1, -1):
        va = pe.off2va(start)
        if va is None:
            continue
        for ins in md.disasm(pe.d[start:start + 1 + window + 8], va):
            if ins.address + ins.size == disp_va:
                if want in ins.op_str.lower():
                    return ins
            if ins.address + ins.size > disp_va:
                break
    return None


def scan_code(pe, target, max_hits=None):
    """Verified disp32 memory accesses of `target` inside every executable section."""
    pat = struct.pack("<I", target)
    hits = []
    for nm, sv, vsz, ptr, rawsz, _ in pe.sections(executable=True):
        blob = pe.d[ptr:ptr + rawsz]
        i = 0
        while True:
            p = blob.find(pat, i)
            if p < 0:
                break
            hits.append(sv + p)          # VA of the disp32 field itself
            i = p + 1
    verified, unverified = [], []
    for disp_va in hits:
        ins = verify_site(pe, disp_va, target)
        (verified if ins else unverified).append((disp_va, ins))
    return hits, verified, unverified


def scan_pointers(pe, target):
    """Stored-pointer sites (tables, vtables, jump tables) in non-executable sections."""
    pat = struct.pack("<I", target)
    out = []
    for nm, sv, vsz, ptr, rawsz, chars in pe.sections(executable=False):
        blob = pe.d[ptr:ptr + rawsz]
        i = 0
        while True:
            p = blob.find(pat, i)
            if p < 0:
                break
            out.append((nm, sv + p))
            i = p + 1
    return out


def main():
    ap = argparse.ArgumentParser(prog="fc3_reloc_xref.py", add_help=True)
    ap.add_argument("path")
    ap.add_argument("targets", nargs="+")
    ap.add_argument("--mode", choices=["code", "reloc", "both"], default="code")
    ap.add_argument("--max-print", type=int, default=40)
    ap.add_argument("--verify-limit", type=int, default=0, help="0 = verify every hit")
    ap.add_argument("--window", type=int, default=15)
    a = ap.parse_args()

    pe = PE(a.path)
    print("%s  machine=%s  imagebase=0x%x  sizeofimage=0x%x  entry=0x%x  %d sections"
          % (a.path, IMAGE_FILE_MACHINE_NAMES.get(pe.machine, hex(pe.machine)), pe.base,
             pe.sizeofimage, pe.base + pe.entry, pe.nsec))
    for nm, sv, vsz, ptr, rawsz, chars in pe.sections():
        print("   %-8s va=0x%08x vsz=0x%08x raw=0x%08x%08x%s%s"
              % (nm, sv, vsz, ptr, rawsz,
                 " X" if chars & 0x20000000 else "", " W" if chars & 0x80000000 else ""))

    for t in a.targets:
        target = int(t, 16)
        print("\n== global 0x%08x  %s" % (target, repr(pe.cstr(target))))
        if a.mode in ("code", "both"):
            hits, verified, unverified = scan_code(pe, target, )
            if a.verify_limit:
                keep = verified[:a.verify_limit]
                verified = [(v, i) for v, i in keep if i] + [(v, None) for v, i in verified[a.verify_limit:]]
            print("   disp32 field hits in executable sections: %d" % len(hits))
            print("   verified instructions: %d   rejected (no instruction ends at the field): %d"
                  % (sum(1 for _, i in verified if i), len(unverified)))
            shown = 0
            for disp_va, ins in verified:
                if shown >= a.max_print:
                    break
                shown += 1
                text = "%s %s" % (ins.mnemonic, ins.op_str) if ins else "(not verified)"
                print("      instr 0x%08x  disp field 0x%08x  %s"
                      % (ins.address if ins else 0, disp_va, text))
            if unverified:
                print("      rejected sample:", ", ".join("0x%08x" % v for v, _ in unverified[:8]))
            ptrs = scan_pointers(pe, target)
            print("   stored-pointer sites in non-executable sections: %d" % len(ptrs))
            for nm, va in ptrs[:a.max_print]:
                print("      %s 0x%08x" % (nm, va))
        if a.mode in ("reloc", "both"):
            relocs = pe.reloc_entries()
            rl = [(f, tv, ty) for f, tv, ty in relocs if tv == target]
            print("   relocation entries: %d; patch sites whose stored value points at the global: %d"
                  % (len(relocs), len(rl)))
            for f, tv, ty in rl[:a.max_print]:
                print("      patch site 0x%08x (%s) stores 0x%08x" % (f, ty, tv))


if __name__ == "__main__":
    main()
