import struct, hashlib, datetime, sys, os

FILES = [r"H:/Uplay/Far Cry 3/bin/FC3.dll",
         r"H:/Uplay/Far Cry 3/bin/FC3_d3d11.dll",
         r"H:/Uplay/Far Cry 3/bin/farcry3_d3d11.exe"]

def pe_info(d):
    pe = struct.unpack_from("<I", d, 0x3c)[0]
    mach = struct.unpack_from("<H", d, pe+4)[0]
    nsec = struct.unpack_from("<H", d, pe+6)[0]
    ts = struct.unpack_from("<I", d, pe+8)[0]
    magic = struct.unpack_from("<H", d, pe+24)[0]
    opt = 224 if magic == 267 else 240
    ep = struct.unpack_from("<I", d, pe+24+16)[0]
    base = struct.unpack_from("<I", d, pe+24+28)[0]
    so = pe + 24 + opt
    secs = {}
    for i in range(nsec):
        nm = d[so+i*40:so+i*40+8].rstrip(b"\0").decode(errors="replace")
        vs, va, rs, rp = struct.unpack_from("<IIII", d, so+i*40+8)
        secs[nm] = (base+va, vs, rs, rp)
    dirs = pe + 24 + 96
    rt_rsrc = struct.unpack_from("<II", d, dirs+2)[1]
    return dict(mach=mach, nsec=nsec, ts=ts, magic=magic, ep=ep, base=base, secs=secs, rsrc=rt_rsrc)

def version_strings(d, info):
    out = {}
    if ".rsrc" not in info["secs"]:
        return out
    sva, vs, rs, rp = info["secs"][".rsrc"]
    blob = d[rp:rp+rs]
    i = 0
    while True:
        i = blob.find(b"VS_VERSION_INFO", i+1)
        if i < 0:
            break
        base = i - (i % 4)
        if base < 4:
            continue
        ln, vk = struct.unpack_from("<HH", blob, base)
        seg = blob[base:base+max(ln, 400)]
        for key in ("FileVersion", "ProductVersion", "OriginalFilename", "ProductName",
                    "FileDescription", "CompanyName"):
            k = seg.find(key.encode("utf-16-le"))
            if k >= 0:
                raw = seg[k+len(key):]
                raw = raw.split(b"\0\0", 1)[0]
                out[key] = raw.decode("utf-16-le", errors="replace").strip("\0")
        m = None
        for off in range(base, min(base+120, len(seg))):
            if seg[off:off+15] == b"VS_VERSION_INFO":
                m = off+15
                break
        if m:
            while m % 4:
                m += 1
            if m+52 <= len(blob):
                v = struct.unpack_from("<4I", blob, m+40)
                out["fixed"] = "%d.%d.%d.%d / %d.%d.%d.%d" % v
        break
    return out

for p in FILES:
    d = open(p, "rb").read()
    info = pe_info(d)
    print("== " + os.path.basename(p))
    print("  size=%d sha256=%s" % (len(d), hashlib.sha256(d).hexdigest()))
    print("  mach=%04x magic=%d nsec=%d EP=%08x base=%08x tstamp=%s" %
          (info["mach"], info["magic"], info["nsec"], info["ep"], info["base"],
           datetime.datetime.utcfromtimestamp(info["ts"]).isoformat()))
    for k, v in info["secs"].items():
        print("   %-8s VA=%08x vsize=%-9d rawsize=%-9d rawptr=%08x" % (k, v[0], v[1], v[2], v[3]))
    print("  version " + repr(version_strings(d, info)))
