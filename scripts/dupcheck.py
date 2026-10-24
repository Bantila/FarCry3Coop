"""Are the 'new' mod files byte copies of vanilla files stored under another name hash?"""
import csv, hashlib, os, collections

W = r"E:\FarCryCoop\Work\fc3"


def md5(p):
    h = hashlib.md5()
    with open(p, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


new = [r for r in csv.DictReader(open(os.path.join(W, "mod", "compare.tsv"), encoding="utf-8"), delimiter="\t")
       if r["status"] == "new"]
sizes = collections.defaultdict(list)
for r in new:
    sizes[os.path.getsize(r["mod_path"])].append(r)

hits = collections.Counter()
examples = {}
for v in ("fc3_main", "multicommon", "common", "patch", "fc3_main_vistas"):
    for root, _, fs in os.walk(os.path.join(W, v)):
        for f in fs:
            p = os.path.join(root, f)
            s = os.path.getsize(p)
            if s in sizes:
                m = md5(p)
                for r in sizes[s]:
                    if r.get("_md5") is None:
                        r["_md5"] = md5(r["mod_path"])
                    if r["_md5"] == m and not r.get("_dup"):
                        r["_dup"] = v
                        hits[(r["mod_archive"], v)] += 1
                        examples.setdefault((r["mod_archive"], v), (r["mod_path"], p))

total = collections.Counter(r["mod_archive"] for r in new)
print("new files per mod archive:", dict(total))
print("byte copies of vanilla files under another hash:", dict(hits))
for k, (a, b) in examples.items():
    print(" example", k, a, "==", b)
