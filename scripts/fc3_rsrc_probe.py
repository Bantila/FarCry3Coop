import sys, struct, hashlib, re
src = r"H:/Uplay/Far Cry 3/bin/farcry3_d3d11.exe"
blob = open(src, "rb").read()
pe_off = struct.unpack_from("<I", blob, 0x3c)[0]
nsec = struct.unpack_from("<H", blob, pe_off+6)[0]
opt = 224 if struct.unpack_from("<H", blob, pe_off+24)[0] == 267 else 240
so = pe_off + 24 + opt
rsrc = None
for i in range(nsec):
    nm = blob[so+i*40:so+i*40+8].rstrip(b"\0")
    vs, va, rs, rp = struct.unpack_from("<IIII", blob, so+i*40+8)
    if nm == b".rsrc":
        rsrc = blob[rp:rp+rs]
print("rsrc bytes", len(rsrc))

# locate embedded MZ/PE headers
offs = [m.start() for m in re.finditer(rb"MZ\x90", rsrc)]
offs += [m.start() for m in re.finditer(rb"MZ", rsrc)]
offs = sorted(set(offs))
print("MZ candidates:", len(offs), offs[:10])
cands = []
for o in offs:
    try:
        e_lfanew = struct.unpack_from("<I", rsrc, o+0x3c)[0]
        if rsrc[o+e_lfanew:o+e_lfanew+4] != b"PE\x00\x00":
            continue
        mach = struct.unpack_from("<H", rsrc, o+e_lfanew+4)[0]
        ns = struct.unpack_from("<H", rsrc, o+e_lfanew+6)[0]
        ts = struct.unpack_from("<I", rsrc, o+e_lfanew+8)[0]
        ep = struct.unpack_from("<I", rsrc, o+e_lfanew+16)[0]
        szopt = struct.unpack_from("<H", rsrc, o+e_lfanew+20)[0]
        if mach in (0x14c, 0x8664) and szopt in (224, 240) and ns and ns < 12:
            cands.append((o, mach, ns, ts, ep, e_lfanew, szopt))
    except Exception as ex:
        pass
import datetime
for o, mach, ns, ts, ep, e_lfanew, szopt in cands[:10]:
    print("cand off=%d mach=%04x nsec=%d tstamp=%s EP=%08x" %
      (o, mach, ns, datetime.datetime.utcfromtimestamp(ts).isoformat(), ep))

# version info from VS_VERSION_INFO resource
def u16(x):
    return x.decode("utf-16-le", errors="replace")
idx = rsrc.find(b"VS_VERSION_INFO")
print("VS_VERSION_INFO found at", idx)
if idx >= 0:
    base = idx - (idx % 4)
    for cand in (idx-2, idx, idx-4):
        pass
    seg = rsrc[base:base+600]
    for key in ("FileVersion","ProductVersion","FileVersion","OriginalFilename","ProductName",
                "FileDescription","CompanyName"):
        k = seg.find(key.encode("utf-16-le"))
        if k >= 0:
            raw = seg[k+len(key):k+len(key)+120]
            parts = raw.split(b"\0\0")
            val = u16(parts[0]) if parts else ""
            print("%s = %r" % (key, val))
    fixed = seg.find(b"VS_VERSION_INFO")
    # fixed file info block: binary values after key
    m = re.search(rb"VS_VERSION_INFO\0+", seg)
    if m:
        p = m.end()
        p += p % 4
        if p+52 <= len(seg):
            v = struct.unpack_from("<IIII", seg, p+40)
            print("fixed ms=%d.%d.%d.%d ls=%d.%d.%d.%d" % v)
        else:
            print("fixed block not reachable, p=", p, "len seg", len(seg))
