"""Add names from FCBConverter's file name list to the hashed files that names.tsv left unnamed."""
import os

ROOT = r"E:\FarCryCoop\Work\fc3"
ARCHIVES = ("fc3_main", "multicommon", "patch", "common", "fc3_main_vistas", r"mod\patch", r"mod\fc3_main_vistas")
LIST = r"E:\FarCryCoop\Tools\fcbconverter-20230711\FCBConverter\FCBConverterFileNames.list"

T = []
for i in range(256):
    c = i
    for _ in range(8):
        c = (c >> 1) ^ (0xD800000000000000 if c & 1 else 0)
    T.append(c)


def h(s):
    x = 0
    for b in s.encode("utf-8", "replace"):
        x = T[(x & 0xFF) ^ b] ^ (x >> 8)
    return f"{x:016X}"


files = {}
for a in ARCHIVES:
    for root, _, fs in os.walk(os.path.join(ROOT, a)):
        for f in fs:
            stem = f.split(".")[0].upper()
            if len(stem) == 16:
                files.setdefault(stem, set()).add(a)

known = {}
for line in open(os.path.join(ROOT, "names.tsv"), encoding="utf-8"):
    p = line.rstrip("\n").split("\t")
    if len(p) >= 2 and p[0] != "hash":
        known[p[0]] = p[1]

added = {}
with open(LIST, encoding="utf-8", errors="replace") as fh:
    for line in fh:
        name = line.strip()
        if not name:
            continue
        k = h(name.lower().replace("/", "\\"))
        if k in files and k not in known and k not in added:
            added[k] = name

with open(os.path.join(ROOT, "names_ext.tsv"), "w", encoding="utf-8", newline="\n") as out:
    out.write("hash\tname\tarchives\tsource\n")
    for k in sorted(set(known) | set(added)):
        src = "manifest" if k in known else "fcbconverter"
        out.write(f"{k}\t{known.get(k) or added[k]}\t{','.join(sorted(files.get(k, ())))}\t{src}\n")

print("hashed files:", len(files), "named before:", len(known), "added:", len(added),
      "still unnamed:", len(set(files) - set(known) - set(added)))
exts = {}
for n in added.values():
    e = os.path.splitext(n)[1].lower()
    exts[e] = exts.get(e, 0) + 1
print(sorted(exts.items(), key=lambda kv: -kv[1])[:15])
