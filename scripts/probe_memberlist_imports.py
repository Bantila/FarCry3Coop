#!/usr/bin/env python
"""probe_memberlist_imports.py - read-only. Which UPLAY_* does FC3_d3d11.dll import (from which dll),
and the IAT thunk RVA of the party member-list getters, so callers can be xrefed next.
Usage: python -I scripts/probe_memberlist_imports.py
"""
import sys
try:
    import pefile
except ImportError:
    sys.stderr.write("need pefile\n"); sys.exit(3)
DLL = r"H:\FarCryCoop\TestFC3_105\bin\FC3_d3d11.dll"
d = pefile.PE(DLL)
base = d.OPTIONAL_HEADER.ImageBase
WANT = {"UPLAY_PARTY_GetFullMemberList", "UPLAY_PARTY_GetInGameMemberList",
        "UPLAY_PARTY_IsPartyLeader", "UPLAY_PARTY_IsInParty", "UPLAY_USER_IsConnected",
        "UPLAY_SetGameSession", "UPLAY_USER_SetGameSession", "UPLAY_ClearGameSession"}
print("machine", hex(d.FILE_HEADER.Machine), "base", hex(base))
thunks = {}
for imp in d.DIRECTORY_ENTRY_IMPORT:
    dllname = imp.dll.decode(errors="replace")
    for e in imp.imports:
        nm = e.name.decode(errors="replace") if e.name else ("ord%d" % e.ordinal)
        if nm.startswith("UPLAY_"):
            mark = " <==" if nm in WANT else ""
            if nm in WANT:
                thunks[nm] = e.address  # IAT slot VA
            print("%-22s  %-40s  iat_va=0x%x rva=0x%x%s" % (
                dllname, nm, e.address, e.address - base, mark))
print("\nWANT thunks found:", len(thunks))
import json, os
out = r"D:\Projects\Co-op Anything\FarCry3Coop-bantila\local\scratch\memberlist_thunks.json"
json.dump({k: v for k, v in thunks.items()}, open(out, "w"), indent=0)
print("saved thunks ->", out)
