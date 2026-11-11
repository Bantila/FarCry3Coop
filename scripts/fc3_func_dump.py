"""Dump a function body from an FC3 PE: embedded strings, data-address immediates, and call targets.

Read-only. Used to understand the 1.06 launch bootstrap without a disassembler.

Usage: python -I scripts/fc3_func_dump.py <pe file> <hex va> [more vas...]
"""
import re
import struct
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

sys.path.insert(0, r"D:/Projects/Co-op Anything/FarCry3Coop-bantila/scripts")
from fc3_addrmap import PE  # noqa: E402


def body_of(pe, va, limit=3000):
    off = pe.va2off(va)
    body = pe.d[off:off + limit]
    end = None
    k = 0
    while k < len(body) - 1:
        if body[k] == 0xC3 and body[k + 1] == 0xCC:
            end = k + 1
            break
        k += 1
    return off, (body[:end] if end is not None else body)


def clean(s):
    return "".join(ch if 0x20 <= ord(ch) < 0x7F else "." for ch in s)


def dump(pe, va, limit=3000):
    off, body = body_of(pe, va, limit)
    print("== 0x%08x raw=0x%x len=%d" % (va, off, len(body)))
    print("   prologue: " + " ".join("%02X" % b for b in body[:48]))
    strs = [b.rstrip(b"\0").decode(errors="replace") for b in re.findall(rb"[ -~]{4,64}\x00", body)]
    print("   inline strings:", strs[:30])
    seen = []
    for j in range(0, len(body) - 5):
        op = body[j]
        if op == 0x68 or 0xB8 <= op <= 0xBF:
            v = struct.unpack_from("<I", body, j + 1)[0]
            o = pe.va2off(v)
            if o is not None and not pe.in_text(v):
                s = pe.d[o:o + 64].split(b"\0")[0].decode(errors="replace")
                if (v, s) not in [(x[0], x[2]) for x in seen]:
                    seen.append((v, j, clean(s)))
    for v, j, s in seen[:30]:
        print("     imm 0x%08x at +0x%04x -> %r" % (v, j, s[:60]))
    calls = []
    for j in range(0, len(body) - 5):
        if body[j] == 0xE8:
            t = struct.unpack_from("<i", body, j + 1)[0]
            calls.append((j, (va + j + 5 + t) & 0xFFFFFFFF))
    print("   calls (%d): %s" % (len(calls), ", ".join("+0x%04x->0x%08x" % (a, b) for a, b in calls[:24])))
    jmp = []
    for j in range(0, len(body) - 5):
        if body[j] == 0xFF and body[j + 1] in (0x15, 0x25):
            v = struct.unpack_from("<I", body, j + 2)[0]
            o = pe.va2off(v)
            nm = ""
            if o is not None:
                nm = clean(pe.d[o:o + 32].split(b"\0")[0].decode(errors="replace"))
            jmp.append((j, v, nm))
    print("   indirect calls (%d): %s" % (len(jmp), ", ".join("+0x%04x 0x%08x %s" % (a, b, c) for a, b, c in jmp[:24])))
    thunks = [j for j in range(0, len(body) - 6) if body[j] == 0xFF and body[j + 1] == 0x15]
    print("   end sentinel: %s" % (" ".join("%02X" % b for b in body[-12:])) if body else "")


if __name__ == "__main__":
    pe = PE(sys.argv[1])
    for a in sys.argv[2:]:
        dump(pe, int(a, 16))
        print()
