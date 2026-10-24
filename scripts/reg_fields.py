"""List reflected field registrations in a code range: 'push <offset>; push <"name">' pairs.

Usage: python -I reg_fields.py <dll> <start_va> <end_va>
Prints, in code order, every pushed string and the small immediate pushed right after it (the field offset).
"""
import re, struct, sys, os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fc3_addrmap import PE

pe = PE(sys.argv[1])
lo, hi = int(sys.argv[2], 16), int(sys.argv[3], 16)
o0, o1 = pe.va2off(lo), pe.va2off(hi)
code = pe.d[o0:o1]
for m in re.finditer(rb"\x68(....)", code, re.S):
    v = struct.unpack("<I", m.group(1))[0]
    so = pe.va2off(v)
    if so is None or pe.in_text(v):
        continue
    s = pe.d[so:so + 64].split(b"\0")[0]
    if len(s) < 3 or not all(32 <= c < 127 for c in s):
        continue
    nxt = code[m.end():m.end() + 6]
    off = None
    if nxt[:1] == b"\x6a":
        off = nxt[1]
    elif nxt[:1] == b"\x68":
        off = struct.unpack("<I", nxt[1:5])[0]
    print(f"0x{lo + m.start():08x}  {s.decode():40s} next push: {hex(off) if off is not None else '-'}")
