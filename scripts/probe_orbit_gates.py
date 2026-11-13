#!/usr/bin/env python
"""probe_orbit_gates.py - read-only: disassemble the prologues of the orbit-API gate functions
in the real uplay_r1_loader.dll to confirm the cdecl int(void) convention before faking them.
Usage: python -I scripts/probe_orbit_gates.py
"""
import sys
try:
    import pefile, capstone
except ImportError as e:
    sys.stderr.write("need pefile+capstone\n"); sys.exit(3)

DLL = r"H:\FarCryCoop\TestFC3_105\bin\real\uplay_r1_loader.dll"
TARGETS = [
    "UPLAY_USER_IsConnected",
    "UPLAY_PARTY_IsInParty",
    "UPLAY_PARTY_IsPartyLeader",
    "UPLAY_PARTY_GetFullMemberList",
    "UPLAY_PARTY_GetInGameMemberList",
    "UPLAY_USER_GetAccountId",
    "UPLAY_PARTY_Init",
]
d = pefile.PE(DLL)
base = d.OPTIONAL_HEADER.ImageBase
exports = {}
for e in d.DIRECTORY_ENTRY_EXPORT.symbols:
    if e.name:
        exports[e.name.decode()] = e.address
md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
md.detail = False
def off(rva):
    return d.get_offset_from_rva(rva)
out = []
for name in TARGETS:
    if name not in exports:
        out.append("%-32s  NOT EXPORTED" % name); continue
    rva = exports[name]
    fo = off(rva)
    if fo is None:
        out.append("%-32s  no file offset (forwarded/ord)" % name); continue
    code = d.get_data(rva, 16)
    out.append("%-32s  rva=0x%x" % (name, rva))
    for ins in md.disasm(code, base + rva):
        out.append("      0x%x: %-8s %s" % (ins.address, ins.mnemonic, ins.op_str))
        if ins.mnemonic in ("ret","int3","jmp") and len([x for x in out[-1:]]) :
            pass
        if ins.mnemonic == "ret":
            break
data = "\n".join(out) + "\n"
sys.stdout.buffer.write(data.encode("utf-8"))
