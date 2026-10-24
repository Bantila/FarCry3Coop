import struct, sys

for path in sys.argv[1:]:
    b = open(path, "rb").read()
    magic, ver, flags, u0c, u10, count = struct.unpack_from("<6I", b, 0)
    end = 24 + count * 20
    print(path, "size", len(b), "magic %08X" % magic, "ver", ver, "flags %08X" % flags,
          "u0C", u0c, "u10", u10, "entries", count, "index end", end, "tail", len(b) - end)
    print("  tail bytes:", b[end:end + 64].hex())
    schemes = {}
    for i in range(min(count, 100000)):
        a, bb, c, d, e = struct.unpack_from("<5I", b, 24 + i * 20)
        s = c & 3
        schemes[s] = schemes.get(s, 0) + 1
        if i < 3:
            print("  entry", i, "hash %08X%08X" % (a, bb), "usize", c >> 2, "scheme", s,
                  "off", (d << 2) | (e >> 30), "csize", e & 0x3FFFFFFF)
    print("  schemes", schemes)
