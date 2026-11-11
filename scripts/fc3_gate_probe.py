"""Read-only gate probe on the FC3 1.06 test copy (no bytes are written anywhere).

Ports the locator logic from the upper-fork scripts (fc3_addrmap.PE + patch_dll.find_sites,
PARTY_LOOP, INSTANCE_MUTEX) so the same analysis runs on the owner's Uplay 1.06 build, and
adds the quick-launch string table plus a copy-integrity check.

Usage: python -I scripts/fc3_gate_probe.py [dir1 dir2 ...]
Default target: H:/FarCryCoop/TestFC3/bin
"""
import hashlib
import os
import re
import sys

sys.path.insert(0, r"D:/Projects/Co-op Anything/FarCry3Coop-bantila/scripts")
from fc3_addrmap import PE  # noqa: E402

TABLE = bytes.fromhex("fc8e0200fd8e0200fe8e0200")  # loc ids 167676..167678, *_END_OF_GAME_INSUFFICIENT_PLAYERS
PARTY_LOOP = re.compile(rb"\xe8....\x8b\xf0\x33\xdb\x39\x1e(\x76)\x3c\x8b\x46\x04\x8b\x04\x98\x85\xc0\x74", re.S)
INSTANCE_MUTEX = re.compile(rb"\x68\x01\x00\x1f\x00\xff\x15....(?:\x3b\xc3|\x85\xc0|\x3b\xc6|\x3b\xc7)(\x0f\x85)", re.S)
QUICK = ["-host", "-client", "-login", "-coop", "-offline", "-sessionuid", "-dedicated", "Missing -login or -ip"]
UPSTREAM = r"H:/Uplay/Far Cry 3/bin"
MD5 = {
    "FC3_d3d11.dll": "916c6d4b876d8be5f0ad68f50719a838",
    "FC3.dll": "5742de2aaa76935d46947bf89e2e2eb7",
    "farcry3_d3d11.exe": "47d4c992b0e82b7d52cc48e8d1bd9119",
}


def function_start(pe, off):
    """Walk back from a code offset to 'push ebp; mov ebp, esp' after ret/padding."""
    k = off
    while k > 16:
        if pe.d[k:k + 3] == b"\x55\x8b\xec" and (pe.d[k - 1] in (0xCC, 0xC3, 0x90) or pe.d[k - 3] == 0xC2):
            return k
        k -= 1
    raise ValueError("function start not found")


def find_sites(pe):
    i = pe.d.find(TABLE)
    n = pe.d.count(TABLE)
    if i < 0 or n != 1:
        return None, [], "table hits=%d" % n
    refs = pe.code_refs(pe.off2va(i))
    if len(refs) != 1:
        return None, [], "table refs=%d" % len(refs)
    start = pe.off2va(function_start(pe, refs[0]))
    t0, t1, tp, ts = pe.text
    text = pe.d[tp:tp + ts]
    sites = []
    for j in range(len(text) - 5):
        if text[j] == 0xE8 and (t0 + j + 5 + struct_unpack(text, j + 1)) & 0xFFFFFFFF == start:
            sites.append(tp + j)
    return start, sites, ""


def struct_unpack(data, off):
    import struct
    return struct.unpack_from("<i", data, off)[0]


def md5(path):
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def probe(dll_dir):
    for name in ("FC3.dll", "FC3_d3d11.dll"):
        path = os.path.join(dll_dir, name)
        if not os.path.isfile(path):
            print("%-14s MISSING at %s" % (name, path))
            continue
        pe = PE(path)
        tva, tend, tptr, tsize = pe.text
        print("== %s (%s)" % (dll_dir, name))
        print("   size=%d base=0x%x .text va=0x%x-0x%x raw=%d" % (len(pe.d), pe.base, tva, tend, tsize))
        start, sites, note = find_sites(pe)
        if start is None:
            print("   insufficient-players gate: NOT LOCATED (%s)" % note)
        else:
            print("   insufficient-players gate: function 0x%08x, call sites (%d): %s" % (
                start, len(sites), ", ".join("0x%08x" % pe.off2va(s) for s in sites)))
        party = PARTY_LOOP.findall(pe.d)
        print("   party-loop jbe candidates (%d): %s" % (len(party), ", ".join("0x%08x" % pe.off2va(m.start(1)) for m in PARTY_LOOP.finditer(pe.d))))
        mx = [m.start(1) for m in INSTANCE_MUTEX.finditer(pe.d)]
        print("   instance-mutex jnz rel32 (%d): %s" % (len(mx), ", ".join("0x%08x" % pe.off2va(p) for p in mx)))
        for s in QUICK:
            v = pe.find_cstring(s)
            print("   %-18s %s" % (s, ", ".join("0x%08x" % a for a in v) if v else "absent"))
        print("   md5=%s %s" % (md5(path), "MATCH upstream 1.06" if md5(path) == MD5.get(name) else "DIFFERS from recorded 1.06 md5"))
        print()


if __name__ == "__main__":
    dirs = sys.argv[1:] or [r"H:/FarCryCoop/TestFC3/bin"]
    for d in dirs:
        probe(d)
