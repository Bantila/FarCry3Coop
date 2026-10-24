import os, re, shutil, sys

ROOT = r"E:\FarCryCoop\Work\fc3"
ARCHIVES = ("fc3_main", "multicommon", "patch", "common")
OUT = os.path.join(ROOT, "named")
TEXT_EXT = (".lua", ".xml")

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


# hash -> {archive: path}
files = {}
for a in ARCHIVES:
    for root, _, fs in os.walk(os.path.join(ROOT, a)):
        for f in fs:
            stem = f.split(".")[0].upper()
            if len(stem) == 16:
                files.setdefault(stem, {})[a] = os.path.join(root, f)

# all IDs from all manifests
rx = re.compile(r'ID="([^"]+)"')
names = set()
manifests = []
for a in ARCHIVES:
    for root, _, fs in os.walk(os.path.join(ROOT, a)):
        for f in fs:
            if f.endswith(".root.xml"):
                manifests.append(os.path.join(root, f))
for m in manifests:
    with open(m, "r", encoding="utf-8", errors="replace") as fh:
        for line in fh:
            for n in rx.findall(line):
                names.add(n)
print("manifests", len(manifests), "unique ids", len(names))

hit = {}
for n in names:
    key = h(n.lower().replace("/", "\\"))
    if key in files:
        hit[key] = n
print("ids matching a file", len(hit), "of", len(files), "hashed files")

os.makedirs(OUT, exist_ok=True)
copied = 0
by_ext = {}
with open(os.path.join(ROOT, "names.tsv"), "w", encoding="utf-8", newline="\n") as tsv:
    tsv.write("hash\tname\tarchives\n")
    for key in sorted(hit):
        n = hit[key]
        tsv.write(f"{key}\t{n}\t{','.join(sorted(files[key]))}\n")
        ext = os.path.splitext(n)[1].lower()
        by_ext[ext] = by_ext.get(ext, 0) + 1
        if ext in TEXT_EXT:
            rel = n.replace("\\", "/").lstrip("/")
            for a, p in files[key].items():
                dst = os.path.join(OUT, a, *rel.split("/"))
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                shutil.copyfile(p, dst)
                copied += 1
print("copied text files", copied)
print(sorted(by_ext.items(), key=lambda kv: -kv[1])[:12])
unmatched = [k for k in files if k not in hit]
print("hashed files without a name", len(unmatched))
