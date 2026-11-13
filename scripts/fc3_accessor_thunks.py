#!/usr/bin/env python3
"""Census the `mov eax, imm32` + `jmp <accessor helper>` thunks inside one PE module.

FC3's static containers are reached through a two-instruction thunk: `mov eax, imm32` loading the
container's base global, followed by `jmp` to an accessor helper (`FC3.dll 0x10004b70`,
`FC3_d3d11.dll 0x10004d70`). The thunks sit in long contiguous runs, so a run boundary is a group
of containers that belong together, and a run's global range is that group's memory block. This
tool enumerates the runs, so a record table or class field can be located inside its own group.
Both 1.06 modules have 3228 thunks in 523 runs (NOTES.md), which is a parity check: a group that
is missing in one module is missing in neither.

Usage: python3 scripts/fc3_accessor_thunks.py <pe_path> [--helper 0x10004b70] [--min-count 3]
        [--range START:END] [--show-va <VA>] [--json]
Prints: per-module total and run count, then each run with its thunk range, thunk count, global
range, and strides. `--show-va` prints only the run that contains that thunk address.
"""
import argparse
import struct
import sys
from bisect import bisect_left, bisect_right

sys.path.insert(0, r"D:/Projects/Co-op Anything/FarCry3Coop-bantila/scripts")
from fc3_addrmap import PE


def scan(pe, helper, lo=None, hi=None):
    """Return sorted (thunk_va, imm32) pairs whose `jmp` resolves to `helper`."""
    tva, tend, tptr, tsize = pe.text
    start, end = tva, tend
    if lo is not None:
        start = max(start, lo)
    if hi is not None:
        end = min(end, hi)
    first, last = pe.va2off(start), pe.va2off(end - 1)
    blob = pe.d[first:last + 1]
    base = start
    out = []
    for i in range(len(blob) - 9):
        if blob[i] != 0xB8:
            continue
        va = base + i
        if blob[i + 5] == 0xE9:
            target = (va + 10 + struct.unpack_from("<i", blob, i + 6)[0]) & 0xFFFFFFFF
        elif blob[i + 5] == 0xEB:
            target = (va + 5 + 2 + struct.unpack_from("<b", blob, i + 6)[0]) & 0xFFFFFFFF
        else:
            continue
        if target == helper:
            out.append((va, struct.unpack_from("<I", blob, i + 1)[0]))
    return out


def runs(hits, max_gap=0x20):
    """Split hits into contiguous runs; a gap larger than max_gap starts a new run."""
    out = []
    cur = []
    for e in hits:
        if cur and e[0] - cur[-1][0] > max_gap:
            out.append(cur)
            cur = []
        cur.append(e)
    if cur:
        out.append(cur)
    return out


def stride(values):
    gaps = sorted(set(b - a for a, b in zip(values, values[1:])))
    return [f"0x{g:x}" for g in gaps]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("path")
    ap.add_argument("--helper", default="0x10004b70")
    ap.add_argument("--min-count", type=int, default=3)
    ap.add_argument("--range", default=None, help="START:END hex, restrict the scan to .text only")
    ap.add_argument("--show-va", default=None, help="print only the run containing this thunk VA")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    helper = int(args.helper, 16)
    lo = hi = None
    if args.range:
        a, b = args.range.split(":")
        lo, hi = int(a, 16), int(b, 16)

    pe = PE(args.path)
    hits = scan(pe, helper, lo, hi)
    groups = runs(hits)
    multi = [g for g in groups if len(g) >= args.min_count]

    print(f"module: {args.path} imagebase 0x{pe.base:x}")
    print(f"accessor helper: 0x{helper:08x}")
    print(f"total thunks: {len(hits)} in {len(groups)} runs "
          f"({len(multi)} runs with at least {args.min_count} thunks)")

    if args.show_va:
        want = int(args.show_va, 16)
        for g in groups:
            if g[0][0] <= want <= g[-1][0]:
                pos = bisect_left([h[0] for h in g], want)
                print(f"run 0x{g[0][0]:08x}..0x{g[-1][0]:08x} count {len(g)} "
                      f"slot {pos} of {len(g)} global 0x{g[pos][1]:08x} "
                      f"globals 0x{min(v for _, v in g):08x}..0x{max(v for _, v in g):08x}")
        return

    if args.json:
        import json
        print(json.dumps({
            "module": args.path,
            "helper": helper,
            "total": len(hits),
            "runs": len(groups),
            "runs_at_least": {
                "min_count": args.min_count,
                "items": [
                    {
                        "thunk_lo": g[0][0],
                        "thunk_hi": g[-1][0],
                        "count": len(g),
                        "global_lo": min(v for _, v in g),
                        "global_hi": max(v for _, v in g),
                        "thunk_strides": stride([v for v, _ in g]),
                        "global_strides": stride([v for _, v in sorted(g, key=lambda x: x[1])]),
                    }
                    for g in multi
                ],
            },
        }, indent=1))
        return

    for g in multi:
        globals_ = [v for _, v in sorted(g, key=lambda x: x[1])]
        print(f"  run 0x{g[0][0]:08x}..0x{g[-1][0]:08x} count {len(g):4d} "
              f"globals 0x{globals_[0]:08x}..0x{globals_[-1]:08x} "
              f"thunk_stride {' '.join(stride([v for v, _ in g]))} "
              f"global_stride {' '.join(stride(globals_))}")


if __name__ == "__main__":
    main()
