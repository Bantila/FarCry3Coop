"""Enumerate session-descriptor parameter records in an FC3 build (read-only).

Far Cry 3 builds 1.05/1.06 register every session/session-parameter descriptor as a record in a
growable record array. In 1.06 the record is created by a call of the shape

    push <name string VA>       ; 68 imm32
    push <type code>            ; 6a imm8   (or 68 imm32 for a code > 0x7f)
    call <descriptor name creator>          ; e8 rel32

FC3_d3d11.dll 1.06 creator: 0x103173f0   (records go to the array pair [0x12852dcc] / count [0x12852dd0])
FC3.dll        1.06 creator: 0x1030f2b0   (records go to the array pair [0x128550cc] / count [0x128550d0])

This script scans the whole .text for `e8 rel32` call sites whose target is one of the given
creators, walks back a short window for the pushed name pointer and type code, and prints the
resolved record list (name, name VA, type code, call site). No writes, no patches, no runtime.

Usage:
  python -I scripts/fc3_param_records.py <pe file> <creator VA> [more creator VAs]
  python -I scripts/fc3_param_records.py <pe file> 0x103173f0 --window 96
  python -I scripts/fc3_param_records.py <pe file> 0x1030f2b0 --filter Search --json

Options:
  --window N   look-back window in bytes for the pushed pair (default 64)
  --filter S   keep only records whose name contains S (case-insensitive)
  --json       machine-readable output instead of the aligned table
  --show-unnamed  also list call sites whose window did not contain a readable name pointer

Known false positives: the look-back window can cross a function boundary and pick up an unrelated
`push imm32` from the previous function. Trust a row only when the window starts at a function head;
cross-check with the registration-block disassembly (fc3_switch_context.py / fc3_func_dump.py).
"""
from __future__ import annotations

import argparse
import json
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fc3_addrmap import PE  # noqa: E402

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass


def read_cstr(pe: PE, va: int, limit: int = 64) -> str | None:
    """Return the printable ASCII/latin-1 C string at `va`, or None if it is not a string."""
    off = pe.va2off(va)
    if off is None:
        return None
    raw = pe.d[off:off + limit]
    end = raw.find(b"\0")
    if end < 0:
        return None
    s = raw[:end]
    if not s or any(b < 0x20 or b > 0x7E for b in s):
        return None
    return s.decode("latin-1")


def scan(pe: PE, creators: set[int], window: int) -> list[dict]:
    text_name = next(nm for nm in pe.sec if nm.startswith(".text"))
    tva, tptr, trawsz = pe.sec[text_name]
    code = pe.d[tptr:tptr + trawsz]

    rows: list[dict] = []
    for i in range(len(code) - 5):
        if code[i] != 0xE8:
            continue
        rel = struct.unpack_from("<i", code, i + 1)[0]
        site = tva + i
        target = site + 5 + rel
        if target not in creators:
            continue

        win_start = max(0, i - window)
        win = code[win_start:i]
        names: list[tuple[int, int, str]] = []   # (string VA, push site, text)
        codes: list[tuple[int, int]] = []
        j = 0
        while j < len(win):
            b = win[j]
            if b == 0x68 and j + 5 <= len(win):
                imm = struct.unpack_from("<I", win, j + 1)[0]
                s = read_cstr(pe, imm)
                if s:
                    names.append((imm, tva + win_start + j, s))
                j += 5
                continue
            if b == 0x6A and j + 2 <= len(win):
                codes.append((tva + win_start + j, win[j + 1]))
                j += 2
                continue
            j += 1

        rows.append({
            "site": site,
            "creator": target,
            "name": names[-1][2] if names else None,
            "name_va": names[-1][0] if names else None,
            "push_site": names[-1][1] if names else None,
            "type_code": codes[-1][1] if codes else None,
            "all_type_codes": [c for _a, c in codes],
        })
    return rows


def main() -> int:
    ap = argparse.ArgumentParser(description="Enumerate FC3 session-descriptor parameter records.")
    ap.add_argument("pe", help="PE file to read (read-only)")
    ap.add_argument("creators", nargs="+", help="creator function VA, e.g. 0x103173f0")
    ap.add_argument("--window", type=int, default=64, help="look-back window in bytes (default 64)")
    ap.add_argument("--filter", default=None, help="keep only names containing this text")
    ap.add_argument("--ident-only", action="store_true", help="keep only identifier-like names")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    ap.add_argument("--show-unnamed", action="store_true", help="also list call sites without a name")
    args = ap.parse_args()

    pe = PE(args.pe)
    creators = {int(a, 16) if a.lower().startswith("0x") else int(a, 16) for a in args.creators}
    rows = scan(pe, creators, args.window)
    if args.ident_only:
        rows = [r for r in rows if r["name"] and IDENT_RE.fullmatch(r["name"])]
    if args.filter:
        needle = args.filter.lower()
        rows = [r for r in rows if r["name"] and needle in r["name"].lower()]
    if not args.show_unnamed:
        rows = [r for r in rows if r["name"]]

    named = [r for r in rows if r["name"]]
    if args.json:
        print(json.dumps({"pe": str(args.pe), "creators": [hex(c) for c in sorted(creators)],
                          "records": rows}, ensure_ascii=False, indent=1))
        return 0

    print(f"# {args.pe}  creators: {', '.join(hex(c) for c in sorted(creators))}  window={args.window}")
    for r in named:
        code = f"0x{r['type_code']:02x}" if r["type_code"] is not None else "-"
        print(f"  0x{r['site']:08x}  call 0x{r['creator']:08x}  {r['name']!r:28} "
              f"string@0x{r['name_va']:08x} push@0x{r['push_site']:08x}  type={code}")
    print(f"# records with a name: {len(named)}   all creator call sites: {len(rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
