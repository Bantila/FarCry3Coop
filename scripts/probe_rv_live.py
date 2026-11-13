#!/usr/bin/env python3
# probe_rv_live.py (read-only): align a live Frida RVA (FC3_d3d11.dll+RVA) against the ON-DISK
# module of the running copy, confirm the file is analyzable (not packed) and that the RV bootstrap
# call site really calls ws2_32!gethostbyname. Usage:
#   python -I scripts/probe_rv_live.py [module.dll] [rva_hex ...]
import sys, pefile
from capstone import Cs, CS_ARCH_X86, CS_MODE_32

DEFAULT_MOD = r"H:\FarCryCoop\TestFC3_105\bin\FC3_d3d11.dll"
DEFAULT_RVAS = ["0x122f759", "0x122f96f", "0x123311e", "0xe5be2c", "0x41a795"]

def main():
    mod = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_MOD
    rvas = [int(x, 16) for x in sys.argv[2:]] or [int(x, 16) for x in DEFAULT_RVAS]
    print("module:", mod)
    pe = pefile.PE(mod, fast_load=False)
    base = pe.OPTIONAL_HEADER.ImageBase
    print("ImageBase = 0x%x ; SizeOfImage = 0x%x ; machine=0x%x" % (base, pe.OPTIONAL_HEADER.SizeOfImage, pe.FILE_HEADER.Machine))

    # locate ws2_32!gethostbyname IAT VA
    iat_va = None; imp_dlls = {}
    for entry in getattr(pe, "DIRECTORY_ENTRY_IMPORT", []):
        dll = entry.dll.decode(errors="replace")
        imp_dlls[dll] = len(entry.imports)
        for sym in entry.imports:
            nm = sym.name.decode(errors="replace") if sym.name else None
            if nm and "gethostbyname" in nm.lower():
                iat_va = sym.address  # IAT slot VA
    print("gethostbyname IAT VA = %s (RVA 0x%x)" % (hex(iat_va) if iat_va else "NOT FOUND",
                                                    (iat_va - base) if iat_va else 0))
    # show a few winsock imports present
    for want in ("ws2_32", "wsock32"):
        for d in imp_dlls:
            if want in d.lower():
                print("  import dll %s (%d syms)" % (d, imp_dlls[d]))

    md = Cs(CS_ARCH_X86, CS_MODE_32)
    for rva in rvas:
        off = pe.get_offset_from_rva(rva)
        if off is None:
            print("\nRVA 0x%x: not mapped" % rva); continue
        back = 0x50
        start = rva - back
        s_off = pe.get_offset_from_rva(start)
        data = pe.__data__[s_off:s_off + back + 0x70]
        va = base + start
        print("\n=== RVA 0x%x  (file off 0x%x, VA 0x%x) ===" % (rva, off, base + rva))
        hits = 0
        for ins in md.disasm(data, va):
            mark = ""
            if ins.mnemonic == "call":
                t = ins.op_str
                # direct call to a VA inside IAT region of gethostbyname
                try:
                    target = int(t.replace("dword ptr [", "").replace("]", ""), 16)
                except Exception:
                    target = None
                if target and iat_va and target == iat_va:
                    mark = "   <== gethostbyname IAT call"; hits += 1
                elif t.startswith("0x"):
                    tv = int(t, 16)
                    if iat_va and abs(tv - iat_va) < 0x2000:
                        mark = "   (near IAT)"
            print("  0x%08x: %-22s %s%s" % (ins.address, ins.bytes.hex(), ins.mnemonic + " " + ins.op_str, mark))
            if ins.address >= base + rva + 0x40:
                break
        print("  -> gethostbyname-direct calls in window:", hits)

if __name__ == "__main__":
    main()
