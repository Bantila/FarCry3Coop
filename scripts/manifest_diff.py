"""Compare a DepotDownloader manifest listing (1.05) with the files of the Steam install (1.06, read only).

Usage: python -I manifest_diff.py <manifest_*.txt> <install dir> <out filelist>
Writes a DepotDownloader -filelist with every file whose size or SHA-1 differs or that is missing.
"""
import hashlib, os, re, sys

manifest, install, out = sys.argv[1:]
rows = []
for line in open(manifest, encoding="utf-8", errors="replace"):
    m = re.match(r"\s*(\d+)\s+(\d+)\s+([0-9a-f]{40})\s+(\d+)\s+(.+?)\s*$", line)
    if m and m.group(4) != "40":  # flag 40 = directory
        rows.append((int(m.group(1)), m.group(3), m.group(5)))


def sha1(p):
    h = hashlib.sha1()
    with open(p, "rb") as f:
        for c in iter(lambda: f.read(1 << 22), b""):
            h.update(c)
    return h.hexdigest()


same, differ, missing = [], [], []
for size, sha, name in rows:
    p = os.path.join(install, name)
    if not os.path.isfile(p):
        missing.append((name, size))
    elif os.path.getsize(p) != size or sha1(p) != sha:
        differ.append((name, size))
    else:
        same.append(name)

print(f"files in 1.05 manifest: {len(rows)}; identical in 1.06: {len(same)}; differ: {len(differ)}; missing: {len(missing)}")
for title, items in (("DIFFER", differ), ("MISSING in 1.06", missing)):
    print(title, f"({sum(s for _, s in items) / 2**20:.0f} MB)")
    for n, s in items:
        print(f"   {s:>12}  {n}")
with open(out, "w", encoding="utf-8", newline="\n") as f:
    for n, _ in differ + missing:
        f.write(n.replace("\\", "/") + "\n")
print("filelist:", out)
