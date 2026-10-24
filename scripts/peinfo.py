import hashlib, struct, sys, datetime

for path in sys.argv[1:]:
    b = open(path, "rb").read()
    pe = struct.unpack_from("<I", b, 0x3C)[0]
    ts = struct.unpack_from("<I", b, pe + 8)[0]
    nsec = struct.unpack_from("<H", b, pe + 6)[0]
    opt = pe + 24
    size_opt = struct.unpack_from("<H", b, pe + 20)[0]
    sec = opt + size_opt
    names = []
    for i in range(nsec):
        name = b[sec + i * 40: sec + i * 40 + 8].rstrip(b"\0").decode("latin1")
        vsize, vaddr, rsize = struct.unpack_from("<III", b, sec + i * 40 + 8)
        names.append(f"{name}:{rsize}")
    # PDB path from the RSDS record
    i = b.find(b"RSDS")
    pdb = b[i + 24: b.find(b"\0", i + 24)].decode("latin1") if i >= 0 else "?"
    guid = b[i + 4: i + 20].hex() if i >= 0 else "?"
    print(path)
    print("  size", len(b), "sha256", hashlib.sha256(b).hexdigest())
    print("  timestamp", datetime.datetime.utcfromtimestamp(ts), "sections", " ".join(names))
    print("  pdb", pdb, "guid", guid)
