#!/usr/bin/env python
"""probe_rv_backend.py - read-only. Locate the RendezVous co-op backend + RV Create/Join in the 1.06 FC3.dll.
- rel32 callers of RVCreateGameSession 0x10cf6790 / RVJoinGameSession 0x10cf6690 (from loader describe() tags)
- code sites that embed pointers to key RendezVous / GameSession strings (the failure/config sites)
Usage: python -I scripts/probe_rv_backend.py
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
def va_off(va):
    rva = va - base
    for s in d.sections:
        if s.VirtualAddress <= rva < s.VirtualAddress + max(s.SizeOfRawData, s.Misc_VirtualSize):
            return s.PointerToRawData + (rva - s.VirtualAddress)
    return None
def find_callers(target):
    out = []; pos = 0
    while True:
        k = traw.find(b"\xe8", pos)
        if k < 0: break
        if k + 5 <= len(traw):
            rel = struct.unpack("<i", traw[k+1:k+5])[0]
            cva = tva + k
            if cva + 5 + rel == target: out.append(cva)
        pos = k + 1
    return out
def find_str_va(needle):
    data = d.get_memory_range(0, d.OPTIONAL_HEADER.SizeOfImage).data if False else None
    # brute: search each mapped raw section for the ascii
    b = needle.encode()
    for s in d.sections:
        raw = s.get_data()
        i = raw.find(b)
        if i >= 0:
            return base + s.VirtualAddress + i
    return None
def find_code_referencing(str_va):
    pat = struct.pack("<I", str_va)
    out = []; pos = 0
    while True:
        k = traw.find(pat, pos)
        if k < 0: break
        out.append(tva + k); pos = k + 1
    return out
for name, va in [("RVCreateGameSession", 0x10cf6790), ("RVJoinGameSession", 0x10cf6690)]:
    print("==== %s @0x%x callers=%d %s ====" % (name, va, len(find_callers(va)), [hex(c) for c in find_callers(va)[:12]]))
for s in ["RendezVousBackEndServices_native", "GameSessionUnsuccessfulJoinSession",
          "GameSessionSearchWithParticipantsResult", "OnlineConfigService.svc", "GetOnlineConfig"]:
    sva = find_str_va(s)
    if sva is None:
        print("==== string %-42s : NOT FOUND ====" % s); continue
    refs = find_code_referencing(sva)
    print("==== string %-42s va=0x%x code-refs=%d %s ====" % (s, sva, len(refs), [hex(c) for c in refs[:12]]))
