"""fc3_switchtable.py -- find launch-argument switch strings in FC3_d3d11.dll (1.06) and every
code site that loads their VA as an immediate (push imm32 / mov r32,imm32).

Usage: python -I games/far-cry-3/tools/fc3_switchtable.py [path]

Read-only analysis. Nothing here is written to the game folder.
"""
import sys, struct, re

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
PATH = sys.argv[1] if len(sys.argv) > 1 else r"H:/FarCryCoop/TestFC3/bin/FC3_d3d11.dll"

d = open(PATH, "rb").read()
e_l = struct.unpack_from("<I", d, 0x3C)[0]
sizeofopt = struct.unpack_from("<H", d, e_l + 20)[0]
base = struct.unpack_from("<I", d, e_l + 24 + 28)[0]
nsec = struct.unpack_from("<H", d, e_l + 6)[0]
sectab = e_l + 24 + sizeofopt
secs = []
for i in range(nsec):
    name = d[sectab + i * 40: sectab + i * 40 + 8].rstrip(b"\0").decode(errors="replace")
    vsize, vaddr, rsize, rptr = struct.unpack_from("<IIII", d, sectab + i * 40 + 8)
    secs.append((name, base + vaddr, max(vsize, rsize), rptr, rsize))
    print("%-8s VA=%08x virt=%08x raw=%08x ptr=%08x" % (name, base + vaddr, vsize, rsize, rptr))


def va2off(va):
    for name, sva, hi, rptr, rsize in secs:
        if sva <= va < sva + hi and (va - sva) < rsize:
            return rptr + (va - sva)
    return None


TEXT = [(s[1], s[1] + s[4], s[3], s[4]) for s in secs if s[0] == ".text"][0]
tva, tend, tptr, tsize = TEXT
text = d[tptr:tptr + tsize]

SWITCHES = ["-host", "-client", "-hostmaster", "-hostgame", "-execline", "-exec", "-dedicator",
            "-profile", "-quickstartup", "-quickdebug", "-demo", "-demoType", "-devfolder",
            "-profilefolder", "-gametype", "-gamemode", "-mapname", "-mapId", "-stageName",
            "-stageOffset", "-stageSize", "-debugFramerateCameras", "-language", "-login", "-coop", "-ip"]

for name in SWITCHES:
    pat = name.encode() + b"\0"
    strings = []
    i = d.find(pat)
    while i >= 0:
        if d[i - 1:i] in (b"\0", b"\x00"):
            o = va2off(i)  # only meaningful if i is inside a mapped raw range
            for nm, sva, hi, rptr, rsize in secs:
                if rptr <= i < rptr + rsize:
                    strings.append((nm, sva + (i - rptr)))
        i = d.find(pat, i + 1)
    refs = []
    for _, va in strings:
        pk = struct.pack("<I", va)
        pos = 0
        while True:
            j = text.find(pk, pos)
            if j < 0:
                break
            prev = text[j - 1]
            if prev == 0x68 or 0xB8 <= prev <= 0xBF:      # push imm32 / mov r32, imm32
                refs.append("0x%08x" % (tva + j - 1))
            pos = j + 1
    print("%-24s strings=%-28s refs=%2d  %s" % (
        name, ",".join("%s:0x%08x" % (m, v) for m, v in strings) or "-", len(refs),
        " ".join(refs[:8])))
