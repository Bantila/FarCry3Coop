"""Compare unpacked mod archives with the unpacked vanilla archives by content (MD5)."""
import hashlib, os, sys, collections

W = r"E:\FarCryCoop\Work\fc3"
VANILLA = ["patch", "common", "fc3_main", "fc3_main_vistas", "multicommon"]
MOD = ["patch", "fc3_main_vistas"]


def stem(name):
    return name.split(".")[0].upper()


def md5(path):
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def index(root):
    out = {}
    for r, _, fs in os.walk(root):
        for f in fs:
            out[stem(f)] = os.path.join(r, f)
    return out


vanilla = {v: index(os.path.join(W, v)) for v in VANILLA}
md5cache = {}


def vmd5(path):
    if path not in md5cache:
        md5cache[path] = md5(path)
    return md5cache[path]


report = open(os.path.join(W, "mod", "compare.tsv"), "w", encoding="utf-8", newline="\n")
report.write("mod_archive\thash\tstatus\tvanilla_archives\tmod_path\n")
for m in MOD:
    mod = index(os.path.join(W, "mod", m))
    stats = collections.Counter()
    types_new = collections.Counter()
    types_changed = collections.Counter()
    for h, p in mod.items():
        where = [v for v in VANILLA if h in vanilla[v]]
        if not where:
            status = "new"
        else:
            mh = md5(p)
            same = [v for v in where if os.path.getsize(vanilla[v][h]) == os.path.getsize(p) and vmd5(vanilla[v][h]) == mh]
            status = "same" if same else "changed"
            where = same or where
        ftype = os.path.basename(os.path.dirname(p))
        stats[status] += 1
        if status == "new":
            types_new[ftype] += 1
        elif status == "changed":
            types_changed[ftype] += 1
        report.write(f"{m}\t{h}\t{status}\t{','.join(where)}\t{p}\n")
    print(f"=== mod {m}: {len(mod)} files", dict(stats))
    print("   new by type:", dict(types_new.most_common(12)))
    print("   changed by type:", dict(types_changed.most_common(12)))
report.close()
