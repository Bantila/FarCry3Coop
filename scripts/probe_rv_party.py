#!/usr/bin/env python
"""probe_rv_party.py - read-only. Disassemble the Rv party-controller functions from the 1.06 FC3.dll
to design the 2-4 roster detour (session 22/24 hooks).
Usage: python -I scripts/probe_rv_party.py [maxbytes]
"""
import sys
try:
    import pefile, capstone
except ImportError:
    sys.stderr.write("need pefile+capstone\n"); sys.exit(3)
DLL = r"H:\Uplay\Far Cry 3\bin\FC3.dll"
d = pefile.PE(DLL)
base = d.OPTIONAL_HEADER.ImageBase
funcs = {
    "FUN_11273650(trusted member list)": 0x11273650,
    "FUN_1006f990(host test)": 0x1006f990,
    "FUN_11218480(join gate)": 0x11218480,
    "FUN_103660e0(member list alt)": 0x103660e0,
}
# string map for annotation
strs = {}
for s in d.sections:
    nm = s.Name.rstrip(b"\x00")
    if nm in (b".rdata", b".data"):
        st = base + s.VirtualAddress; raw = s.get_data(); i = 0
        while i < len(raw):
            j = raw.find(b"\x00", i); run = raw[i:j]
            if len(run) >= 5 and all(32 <= c < 127 for c in run):
                strs[st + i] = run.decode("ascii", "replace")
            i = (j + 1) if j >= 0 else len(raw)
def off_of(va):
    rva = va - base
    for s in d.sections:
        if s.VirtualAddress <= rva < s.VirtualAddress + max(s.SizeOfRawData, s.Misc_VirtualSize):
            return s.PointerToRawData + (rva - s.VirtualAddress)
    return None
md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
maxb = int(sys.argv[1]) if len(sys.argv) > 1 else 160
out = []
for label, va in funcs.items():
    fo = off_of(va)
    if fo is None:
        out.append("%-40s NOT MAPPED" % label); continue
    code = d.get_data(fo, maxb)
    out.append("==== %s @0x%x ====" % (label, va))
    for ins in md.disasm(code, va):
        cmt = ""
        for tok in ins.op_str.replace(",", " ").replace("[", " ").replace("]", " ").split():
            if tok.endswith("h"):
                try: v = int(tok[:-1], 16)
                except ValueError: continue
                if v in strs: cmt = '   ; "%s"' % strs[v][:40]; break
        out.append("  0x%x: %-7s %-30s%s" % (ins.address, ins.mnemonic, ins.op_str, cmt))
        if ins.mnemonic in ("ret",) and "4" in ins.op_str or ins.mnemonic == "ret":
            # stop at first ret to keep output tight
            break
    out.append("")
sys.stdout.buffer.write(("\n".join(out) + "\n").encode("utf-8"))
