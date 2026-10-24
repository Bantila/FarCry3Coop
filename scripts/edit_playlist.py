"""Edit fields of one playlist in a FCBConverter XML of generated\\nomadobjecttemplates.fcb.

Usage: python -I edit_playlist.py <in.converted.xml> <out.converted.xml> "Local Coop" minPlayersInRound=1 matchCountdownInSecs=10
Only Int32 fields; the edited line keeps FCBConverter's format (value-Int32 and BinHex).
"""
import re, struct, sys

src, dst, playlist, *edits = sys.argv[1:]
edits = dict(e.split("=") for e in edits)
lines = open(src, encoding="utf-8").read().split("\n")

anchor = [i for i, l in enumerate(lines) if f'name="name" value-String="{playlist}"' in l]
if len(anchor) != 1:
    raise SystemExit(f"playlist {playlist!r} found {len(anchor)} times")
a = anchor[0]
done = set()
for i in range(a, min(a + 40, len(lines))):  # the playlist's fields follow its name
    for field, value in edits.items():
        if f'name="{field}" value-Int32=' in lines[i] and field not in done:
            v = int(value)
            hexv = struct.pack("<i", v).hex().upper()
            lines[i] = re.sub(r'value-Int32="-?\d+" type="BinHex">[0-9A-F]+<',
                              f'value-Int32="{v}" type="BinHex">{hexv}<', lines[i])
            done.add(field)
missing = set(edits) - done
if missing:
    raise SystemExit(f"fields not found near the playlist: {missing}")
open(dst, "w", encoding="utf-8", newline="\n").write("\n".join(lines))
print(f"{playlist}: set {edits} -> {dst}")
