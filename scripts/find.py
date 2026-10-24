import os, sys

ROOT = r"E:\FarCryCoop\Work\fc3"
T = []
for i in range(256):
    c = i
    for _ in range(8):
        c = (c >> 1) ^ (0xD800000000000000 if c & 1 else 0)
    T.append(c)


def h(s):
    x = 0
    for b in s.encode():
        x = T[(x & 0xFF) ^ b] ^ (x >> 8)
    return f"{x:016X}"


want = {}
for n in sys.argv[1:]:
    want[h(n.lower().replace("/", "\\"))] = n
for a in ("fc3_main", "multicommon", "patch", "common"):
    for root, _, fs in os.walk(os.path.join(ROOT, a)):
        for f in fs:
            k = f.split(".")[0].upper()
            if k in want:
                print(want[k], os.path.join(root, f))
