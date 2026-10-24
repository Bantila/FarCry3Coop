"""Compare FAT v9 entry sets: where does each entry of a mod archive come from?"""
import struct, sys, os

G = r"E:\SteamLibrary\steamapps\common\Far Cry 3\data_win32"
M = r"E:\FarCryCoop\Downloads\fc3-open-world-coop\Far Cry 3\data_win32"
NAMES = r"E:\FarCryCoop\Work\fc3\names.tsv"


def read_fat(path):
    b = open(path, "rb").read()
    count = struct.unpack_from("<I", b, 20)[0]
    out = {}
    for i in range(count):
        a, bb, c, d, e = struct.unpack_from("<5I", b, 24 + i * 20)
        out["%08X%08X" % (a, bb)] = (c >> 2, c & 3, e & 0x3FFFFFFF)  # usize, scheme, csize
    return out


vanilla = {
    "patch": read_fat(os.path.join(G, "patch.fat")),
    "common": read_fat(os.path.join(G, "common.fat")),
    "fc3_main": read_fat(os.path.join(G, r"worlds\fc3_main\fc3_main.fat")),
    "fc3_main_vistas": read_fat(os.path.join(G, r"worlds\fc3_main\fc3_main_vistas.fat")),
    "multicommon": read_fat(os.path.join(G, r"worlds\multicommon\multicommon.fat")),
}
names = {}
for line in open(NAMES, encoding="utf-8"):
    p = line.rstrip("\n").split("\t")
    if len(p) >= 2:
        names[p[0]] = p[1]

for modname, rel in (("patch", "patch.fat"), ("fc3_main_vistas", r"worlds\fc3_main\fc3_main_vistas.fat")):
    mod = read_fat(os.path.join(M, rel))
    print(f"=== mod {modname}: {len(mod)} entries")
    stats = {}
    new = []
    changed_in_patch = []
    for h, info in mod.items():
        where = [k for k, v in vanilla.items() if h in v]
        same = [k for k in where if vanilla[k][h] == info]
        key = ("same:" + ",".join(same)) if same else ("changed:" + ",".join(where) if where else "new")
        stats[key] = stats.get(key, 0) + 1
        if not where:
            new.append(h)
        elif not same and "patch" in where:
            changed_in_patch.append(h)
    for k, v in sorted(stats.items(), key=lambda kv: -kv[1]):
        print(f"  {v:7d}  {k}")
    named_new = [names[h] for h in new if h in names]
    print(f"  new with known names: {len(named_new)}")
    for n in sorted(named_new)[:40]:
        print("    ", n)
    if modname == "patch":
        missing = [h for h in vanilla["patch"] if h not in mod]
        print(f"  vanilla patch entries missing from mod patch: {len(missing)}")
