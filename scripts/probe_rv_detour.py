#!/usr/bin/env python
"""probe_rv_detour.py - read-only. Deepen the 2-4 roster detour design on the 1.06 FC3.dll.
- re-derive misaligned function starts (walk back to a prologue)
- find rel32 callers of the join-gate / trusted-list / member getter
- disasm the member getter and a longer trusted-list body for member field offsets
Usage: python -I scripts/probe_rv_detour.py
"""
import sys, struct
try:
    import pefile, capstone
except ImportError:
    sys.stderr.write("need pefile+capstone\n"); sys.exit(3)
DLL = r"H:\Uplay\Far Cry 3\bin\FC3.dll"
d = pefile.PE(DLL)
base = d.OPTIONAL_HEADER.ImageBase
text = next(s for s in d.sections if s.Name.rstrip(b"\x00") == b".text")
tva = base + text.VirtualAddress
traw = text.get_data()
def off_of(va):
    rva = va - base
    for s in d.sections:
        if s.VirtualAddress <= rva < s.VirtualAddress + max(s.SizeOfRawData, s.Misc_VirtualSize):
            return s.PointerToRawData + (rva - s.VirtualAddress)
    return None
def in_text(va): return tva <= va < tva + text.Misc_VirtualSize
def find_callers(target):
    out = []; pos = 0
    while True:
        k = traw.find(b"\xe8", pos)
        if k < 0: break
        if k + 5 <= len(traw):
            rel = struct.unpack("<i", traw[k+1:k+5])[0]
            cva = tva + k
            if cva + 5 + rel == target:
                out.append(cva)
        pos = k + 1
    return out
md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
def re_align(va, maxback=40):
    # if the 6 bytes at va don't start a sane function, walk back to a common prologue
    fo = off_of(va)
    sig = traw[fo- tva: fo - tva + 6] if in_text(va) else b""
    # try: look back for 55 8B EC (push ebp; mov ebp,esp) or 51/53/56 push regs then sub esp
    for back in range(0, maxback):
        c = va - back
        fo = off_of(c)
        if fo is None: continue
        b0 = d.get_data(fo, 8)
        if b0[:3] == b"\x55\x8b\xec" or b0[:2] == b"\x8b\xff":
            return c
    return va
def disasm(va, n):
    fo = off_of(va)
    if fo is None:
        print("  (not mapped)"); return
    code = d.get_data(fo, n)
    for ins in md.disasm(code, va):
        print("  0x%x: %-7s %s" % (ins.address, ins.mnemonic, ins.op_str))
        if ins.mnemonic == "ret":
            break
for name, va in [("join gate FUN_11218480", 0x11218480),
                 ("trusted list FUN_11273650", 0x11273650),
                 ("member getter 0x10070590", 0x10070590),
                 ("host test FUN_1006f990", 0x1006f990),
                 ("member alt FUN_103660e0", 0x103660e0)]:
    cs = find_callers(va)
    print("==== %s @0x%x  callers=%d %s ====" % (name, va, len(cs), [hex(c) for c in cs[:10]]))
out = []
for name, va in [("member getter 0x10070590", 0x10070590),
                 ("host test FUN_1006f990 aligned", re_align(0x1006f990)),
                 ("member alt FUN_103660e0 aligned", re_align(0x103660e0))]:
    print("\n#### disasm %s ####" % name)
    disasm(va, 90)
