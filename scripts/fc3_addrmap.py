"""Build an address map for one FC3.dll build (1.05 or 1.06) by plain byte scanning.

Finds anchor strings, the code that references them, the callback pushed just before
each reference (the registration pattern seen in FC3.dll), and the absolute globals the
first instructions of each callback read. No Ghidra needed; runs in seconds.

Usage: python -I fc3_addrmap.py FC3.dll out.tsv [--all]
Self-check: python -I fc3_addrmap.py --selftest  (expects the 1.06 DLL at the path below)
"""
import struct, sys, re

DLL_106 = r"E:\SteamLibrary\steamapps\common\Far Cry 3\bin\FC3.dll"
DLL_105 = r"E:\FarCryCoop\Downloads\fc3-1.05\bin\FC3.dll"

# Lua globals and console commands we care about (registered as name + callback)
FUNCS = [
    "GetLocalPlayerId", "GetPlayerInSlot", "GetNumberOfPlayers", "GetSlotForPlayer",
    "CoopTeleportPlayer", "SpawnCoopAI", "CoopGetCharacterName", "CoopDoGetPawnState",
    "GetInvalidEntityId", "TeleportToCurrentObjective", "SetHealth",
]
# data anchors: only the string address and its code references are reported
DATA = [
    "CFCXPlayerService", "NetObject.FCXPlayerService", "OnSpawnPlayer_%u",
    "engine\\settings\\OverrideNetworkConfig.xml", "engine\\settings\\DefaultNetworkConfig.xml",
    "mpdlc1_aegir", "CoopNameplatesUI", "CFCXCoopNameplatesUI", "CRadioTowerPanelComponent",
    "fBlendOutFOVTime", "LanMatchmakingDiscoveryOnLoopbackEnable", "NetEngineType",
    "SearchIdAddress", "patch.dat", "CFCXJoinSessionOperation", "CFCXCreateSessionOperation",
]
# byte blobs patched by scubrah's mod (world bounds for network quantization)
BLOBS = {"bounds1536": bytes.fromhex("55555555555545")}


class PE:
    def __init__(self, path):
        self.d = open(path, "rb").read()
        d = self.d
        pe = struct.unpack_from("<I", d, 0x3C)[0]
        self.base = struct.unpack_from("<I", d, pe + 24 + 28)[0]
        n = struct.unpack_from("<H", d, pe + 6)[0]
        so = pe + 24 + struct.unpack_from("<H", d, pe + 20)[0]
        self.sec = {}
        for i in range(n):
            name = d[so + i * 40: so + i * 40 + 8].rstrip(b"\0").decode()
            vsize, vaddr, rsize, rptr = struct.unpack_from("<IIII", d, so + i * 40 + 8)
            self.sec[name] = (self.base + vaddr, rptr, rsize)
            self.vranges = getattr(self, "vranges", []) + [(self.base + vaddr, self.base + vaddr + max(vsize, rsize))]
        tva, tptr, tsize = self.sec[".text"]
        self.text = (tva, tva + tsize, tptr, tsize)

    def off2va(self, off):
        for va, ptr, size in self.sec.values():
            if ptr <= off < ptr + size:
                return va + off - ptr
        return None

    def va2off(self, va):
        for sva, ptr, size in self.sec.values():
            if sva <= va < sva + size:
                return ptr + va - sva
        return None

    def in_text(self, va):
        return self.text[0] <= va < self.text[1]

    def find_cstring(self, s):
        """VAs of exact NUL-terminated occurrences of s (preceded by NUL or alignment)."""
        pat = s.encode() + b"\0"
        out, i = [], self.d.find(pat)
        while i >= 0:
            if i == 0 or self.d[i - 1] == 0:
                out.append(self.off2va(i))
            i = self.d.find(pat, i + 1)
        return out

    def code_refs(self, va):
        """Offsets in .text of push imm32 (68) / mov r32, imm32 (B8..BF) using va."""
        tva, tend, tptr, tsize = self.text
        text = self.d[tptr: tptr + tsize]
        needle = struct.pack("<I", va)
        out, i = [], text.find(needle)
        while i >= 0:
            if i >= 1 and (text[i - 1] == 0x68 or 0xB8 <= text[i - 1] <= 0xBF):
                out.append(tptr + i - 1)
            i = text.find(needle, i + 1)
        return out

    def callback_for(self, ref_off):
        """Callback registered with the name referenced at ref_off: the closest code push before it.

        Verified by decompiling in both builds:
        1.05: ...; push ebx; push CB; push edi; call; push name; push esi; push edi; call
        1.06: push 0; push CB; call; mov edi, name
        """
        return self.callback_before(ref_off)

    def callback_before(self, ref_off, window=40):
        """Closest 'push imm32' into .text within window bytes before ref_off."""
        best = None
        for k in range(ref_off - 5, ref_off - window, -1):
            if self.d[k] == 0x68:
                v = struct.unpack_from("<I", self.d, k + 1)[0]
                if self.in_text(v):
                    best = v
                    break
        return best

    def globals_read(self, va, length=96):
        """Absolute data addresses read in the first bytes of a function, with displacements seen nearby."""
        off = self.va2off(va)
        code = self.d[off: off + length]
        found = []
        for m in re.finditer(rb"(\xa1|\x8b[\x05\x0d\x15\x1d\x2d\x35\x3d])(....)", code, re.S):
            v = struct.unpack("<I", m.group(2))[0]
            # .data globals may sit in the uninitialized tail (virtual size > raw size)
            if any(lo <= v < hi for lo, hi in self.vranges) and not self.in_text(v):
                found.append(f"0x{v:08x}")
        return found


def build(path, want_all=False):
    pe = PE(path)
    rows = []
    for name in FUNCS + DATA:
        for sva in pe.find_cstring(name):
            refs = pe.code_refs(sva)
            if not refs:
                rows.append((name, f"0x{sva:08x}", "", "", ""))
            for r in refs:
                cb = pe.callback_for(r) if name in FUNCS else None
                g = ",".join(pe.globals_read(cb)) if cb else ""
                rows.append((name, f"0x{sva:08x}", f"0x{pe.off2va(r):08x}", f"0x{cb:08x}" if cb else "", g))
    for name, blob in BLOBS.items():
        i = pe.d.find(blob)
        rows.append((name, f"0x{pe.off2va(i):08x}" if i >= 0 else "", "", "", ""))
    return pe, rows


def write(rows, out):
    with open(out, "w", encoding="utf-8", newline="\n") as f:
        f.write("name\tstring_va\tref_va\tcallback_va\tglobals_read\n")
        for r in rows:
            f.write("\t".join(r) + "\n")


def selftest():
    # known 1.06 facts found by hand with REA/Ghidra on 2026-10-24
    pe, rows = build(DLL_106)
    cbs = {(r[0], r[3]) for r in rows}
    assert ("GetPlayerInSlot", "0x10680ef0") in cbs, rows
    assert ("GetNumberOfPlayers", "0x10681070") in cbs
    assert ("GetLocalPlayerId", "0x1065ef50") in cbs
    assert any(r[0] == "GetNumberOfPlayers" and "0x12804acc" in r[4] for r in rows)
    # known 1.05 facts, decompiled with REA/Ghidra on 2026-10-24
    _, rows = build(DLL_105)
    cbs = {(r[0], r[3]) for r in rows}
    assert ("GetPlayerInSlot", "0x10bad843") in cbs, rows      # int slot -> 64-bit entity id
    assert ("GetNumberOfPlayers", "0x10baba48") in cbs         # no argument -> number
    assert ("CoopGetCharacterName", "0x10badb62") in cbs       # EntityId argument
    assert ("CoopDoGetPawnState", "0x10bad8b5") in cbs         # int argument -> number
    print("selftest ok")


if __name__ == "__main__":
    if sys.argv[1] == "--selftest":
        selftest()
    else:
        _, rows = build(sys.argv[1], "--all" in sys.argv)
        write(rows, sys.argv[2])
        for r in rows:
            print("\t".join(r))
