"""Grep ASCII/UTF-16 strings in a PE's .rdata/.data and report VA + nearby candidates.

Usage: python -I tools/fc3_strgrep.py <pe file> [needle ...]
Default needles: FC3 console/session command candidates.
"""
import sys

sys.path.insert(0, r"D:/Projects/Co-op Anything/FarCry3Coop-bantila/scripts")
from fc3_addrmap import PE  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

DEFAULTS = ["StartGame", "HostGame", "LaunchGame", "StartCoop", "CoopStart", "co-op",
 "StartSession", "CreateSession", "JoinGame", "execLines", "-exec", "numclients",
 "splitscreen", "-world", "LocalCoop", "Local Coop", "PlaylistId", "sessionType",
 "multi_", "hack_", "gfx_No"]


def printable(blob, i):
    j = i
    while j and blob[j - 1] != 0:
        j -= 1
    k = i
    while k < len(blob) and blob[k] != 0:
        k += 1
    raw = blob[j:k]
    if len(raw) < 3 or any(c < 0x20 for c in raw):
        return None
    try:
        return raw.decode("latin-1")
    except UnicodeDecodeError:
        return None


def main(path, needles):
    pe = PE(path)
    d = pe.d
    for name in (".rdata", ".data"):
        if name not in pe.sec:
            continue
        va, ptr, size = pe.sec[name]
        blob = d[ptr:ptr + size]
        for nd in needles:
            pat = nd.encode("latin-1")
            n = 0
            i = blob.find(pat)
            while i >= 0 and n < 6:
                s = printable(blob, i)
                if s:
                    print("%s %s 0x%08x %r" % (name, nd, va + i, s[:80]))
                    n += 1
                i = blob.find(pat, i + 1)


if __name__ == "__main__":
    a = sys.argv[1:]
    main(a[0], a[1:] or DEFAULTS)
