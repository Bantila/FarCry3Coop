import struct
FILES = [r"H:/Uplay/Far Cry 3/bin/FC3.dll", r"H:/Uplay/Far Cry 3/bin/FC3_d3d11.dll",
         r"H:/Uplay/Far Cry 3/bin/farcry3_d3d11.exe"]
for p in FILES:
    d = open(p, "rb").read()
    hits = []
    i = -1
    for _ in range(5):
        i = d.find(b"VS_VERSION_INFO", i+1)
        if i < 0:
            break
        hits.append(i)
    print(p.split("/")[-1], "VS_VERSION_INFO raw offsets:", hits)
    for off in hits[:2]:
        seg = d[off:off+120]
        print("   raw:", seg[:64])
    for key in (b"FileVersion", b"ProductVersion", b"1.06"):
        k = d.find(key)
        print("   key", key, "offset", k)
