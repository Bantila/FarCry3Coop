"""Patch a COPY of FC3.dll / FC3_d3d11.dll (1.05 or 1.06): a co-op session no longer ends with
"The game session ended prematurely because of an insufficient number of players".

The end-session function is found through its loc-id table {167676, 167677, 167678}; every
'call <function>' is replaced with 5 NOPs (mod 262 does the same for 1.05).

Usage:     python -I patch_dll.py <dll copy>      (patches in place, refuses the Steam install)
Self-test: python -I patch_dll.py --selftest      (1.05 result must equal mod 262's DLL byte for byte)
"""
import re, struct, sys, os, shutil, tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fc3_addrmap import PE

TABLE = bytes.fromhex("fc8e0200fd8e0200fe8e0200")  # loc ids 167676..167678, *_END_OF_GAME_INSUFFICIENT_PLAYERS
INSTALL = r"E:\SteamLibrary\steamapps\common"


def function_start(pe, off):
    """Walk back from a code offset to 'push ebp; mov ebp, esp' that follows a ret or padding."""
    k = off
    while k > 16:
        if pe.d[k:k + 3] == b"\x55\x8b\xec" and (pe.d[k - 1] in (0xCC, 0xC3, 0x90) or pe.d[k - 3] == 0xC2):
            return k
        k -= 1
    raise ValueError("function start not found")


def find_sites(pe):
    i = pe.d.find(TABLE)
    if i < 0 or pe.d.find(TABLE, i + 1) >= 0:
        raise ValueError("loc-id table not found exactly once")
    refs = pe.code_refs(pe.off2va(i))
    if len(refs) != 1:
        raise ValueError(f"expected one code reference to the table, found {len(refs)}")
    start = pe.off2va(function_start(pe, refs[0]))
    t0, t1, tp, ts = pe.text
    text = pe.d[tp:tp + ts]
    sites = []
    for j in range(len(text) - 5):
        if text[j] == 0xE8 and (t0 + j + 5 + struct.unpack_from("<i", text, j + 1)[0]) & 0xFFFFFFFF == start:
            sites.append(tp + j)
    return start, sites


def patch(path):
    if os.path.abspath(path).lower().startswith(INSTALL.lower()):
        raise SystemExit("refusing to patch the Steam install; patch a copy")
    pe = PE(path)
    data = bytearray(pe.d)
    start, sites = find_sites(pe)
    for s in sites:
        data[s:s + 5] = b"\x90" * 5
    print(f"{path}: end-session function 0x{start:08x}, NOPed calls: "
          + (", ".join(f"0x{pe.off2va(s):08x}" for s in sites) or "none left"))
    party = find_party_loop(data)
    for p in party:
        data[p] = 0xEB  # jbe -> jmp: skip the Uplay party member loop
    print(f"   party-list loop skipped at: " + (", ".join(f"0x{pe.off2va(p):08x}" for p in party) or "none left"))
    mutex = find_instance_mutex_check(data)
    for p in mutex:
        data[p:p + 6] = b"\x90" * 6  # jnz <ERROR_INSTANCE_MUTEX> -> nothing
    print(f"   single-instance check removed at: " + (", ".join(f"0x{pe.off2va(p):08x}" for p in mutex) or "none left"))
    if data != pe.d:
        tmp = path + ".tmp"
        with open(tmp, "wb") as f:
            f.write(data)
        os.replace(tmp, path)


# Offline coop crash (1.05): FUN_10622c58 loops over the list filled by UPLAY_PARTY_GetFullMemberList.
# Today's Ubisoft Connect no longer serves the party API; the call fails, the list keeps garbage
# (count > 0, bad data pointer) and the loop reads it. The party list is not needed (our own network
# layer gathers the players), so the 'jbe' that skips an empty list becomes an unconditional 'jmp'.
#   call get_list; mov esi,eax; xor ebx,ebx; cmp [esi],ebx; jbe +3c; mov eax,[esi+4]; mov eax,[eax+ebx*4]
PARTY_LOOP = re.compile(rb"\xe8....\x8b\xf0\x33\xdb\x39\x1e(\x76)\x3c\x8b\x46\x04\x8b\x04\x98\x85\xc0\x74", re.S)


def find_party_loop(data):
    return [m.start(1) for m in PARTY_LOOP.finditer(bytes(data))]


# Single-instance check at start-up (1.05 FC3.dll 0x100041ae): OpenMutexA(MUTEX_ALL_ACCESS, FALSE, name);
# a found mutex jumps to ERROR_INSTANCE_MUTEX ("You already have a Far Cry 3 session ... active").
# Removing the jump lets two copies run on one PC (needed for host + client tests; harmless otherwise).
#   push 0x1f0001; call [OpenMutexA]; cmp eax,ebx | test eax,eax; jnz rel32
INSTANCE_MUTEX = re.compile(rb"\x68\x01\x00\x1f\x00\xff\x15....(?:\x3b\xc3|\x85\xc0|\x3b\xc6|\x3b\xc7)(\x0f\x85)", re.S)


def find_instance_mutex_check(data):
    return [m.start(1) for m in INSTANCE_MUTEX.finditer(bytes(data))]


def selftest():
    clean = r"E:\FarCryCoop\Downloads\fc3-1.05\bin"
    mod262 = r"E:\FarCryCoop\Downloads\fc3-solo-offline-coop"
    with tempfile.TemporaryDirectory(dir=r"E:\FarCryCoop\Temp") as tmp:
        for name in ("FC3.dll", "FC3_d3d11.dll"):
            p = os.path.join(tmp, name)
            shutil.copyfile(os.path.join(clean, name), p)
            patch(p)
            ours, theirs = open(p, "rb").read(), open(os.path.join(mod262, name), "rb").read()
            diff = [i for i in range(len(ours)) if ours[i] != theirs[i]]
            # mod 262 + the party-loop jbe -> jmp (1 byte) + the single-instance jnz -> 6 NOPs
            party = [i for i in diff if theirs[i] == 0x76 and ours[i] == 0xEB]
            nops = [i for i in diff if ours[i] == 0x90]
            assert len(party) == 1 and len(nops) == 6 and len(diff) == 7, (name, diff)
            before = open(p, "rb").read()
            patch(p)  # second run must be a no-op
            assert open(p, "rb").read() == before
    for name in ("FC3.dll", "FC3_d3d11.dll"):
        pe = PE(os.path.join(INSTALL, "Far Cry 3", "bin", name))  # read-only
        start, sites = find_sites(pe)
        print(f"1.06 {name}: end-session function 0x{start:08x}, {len(sites)} calls; party loops: {len(find_party_loop(pe.d))}")
        assert sites
    print("selftest ok: 1.05 output = mod 262 + party-loop fix + single-instance check removed")


if __name__ == "__main__":
    if sys.argv[1] == "--selftest":
        selftest()
    else:
        for p in sys.argv[1:]:
            patch(p)
