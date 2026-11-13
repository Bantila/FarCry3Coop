"""Launch the FC3 1.06 private test copy with quick-launch arguments and watch what really runs.

Answers the open blocker question: does launching `TestFC3/bin/farcry3_d3d11.exe` with
`-host <map> -login <name> -coop` run our own copy (arguments preserved), or does it hand off
to the canonical Uplay install and drop the arguments?

Read/writes nothing inside the game folders; only starts a process and then terminates it.

Usage: python -I tools/fc3_launch_probe.py [--args "..."] [--wait 75] [--no-kill]
"""
import argparse
import os
import subprocess
import sys
import time

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

EXE = r"H:/FarCryCoop/TestFC3/bin/farcry3_d3d11.exe"
WATCH = ("farcry3_d3d11.exe", "farcry3.exe", "FC3Updater.exe", "upc.exe", "Upplay.exe")


def snapshot():
    """Return (name, pid, parent pid, command line, executable path) rows via PowerShell CIM."""
    ps = (
        "Get-CimInstance Win32_Process -Filter \"ProcessId>0\" | "
        "Where-Object { $_.Name -match 'farcry|FC3|upc|Upplay' } | "
        "Select-Object Name,ProcessId,ParentProcessId,CommandLine,ExecutablePath | "
        "ConvertTo-Json -Compress"
    )
    r = subprocess.run(["powershell", "-NoProfile", "-Command", ps], capture_output=True, text=True, timeout=120)
    txt = r.stdout.strip()
    if not txt:
        return []
    import json
    try:
        data = json.loads(txt)
    except Exception:
        print("  snapshot parse failed:", txt[:200])
        return []
    if isinstance(data, dict):
        data = [data]
    rows = []
    for d in data:
        rows.append((d.get("Name"), d.get("ProcessId"), d.get("ParentProcessId"),
                     d.get("CommandLine") or "", d.get("ExecutablePath") or ""))
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--exe", default=EXE)
    ap.add_argument("--args", default="-host fc3_main -login h1 -coop")
    ap.add_argument("--wait", type=int, default=75)
    ap.add_argument("--no-kill", action="store_true")
    a = ap.parse_args()

    cmd = [a.exe] + a.args.split()
    print("launch:", " ".join(cmd))
    t0 = time.time()
    p = subprocess.Popen(cmd, cwd=os.path.dirname(a.exe))
    print("pid", p.pid)
    seen = {}
    alive = True
    while time.time() - t0 < a.wait:
        time.sleep(5)
        rc = p.poll()
        rows = snapshot()
        for name, pid, ppid, cl, path in rows:
            key = (name, pid)
            if key not in seen:
                seen[key] = True
                print("  +%5.0fs NEW %-18s pid=%s ppid=%s" % (time.time() - t0, name, pid, ppid))
                print("       path=%s" % path)
                print("       cmd=%s" % cl)
        if rc is not None and alive:
            alive = False
            print("  +%5.0fs parent pid=%s exited with code %s" % (time.time() - t0, p.pid, rc))
        elif alive:
            print("  +%5.0fs parent still running, tracked processes=%d" % (time.time() - t0, len(rows)))
    rc = p.poll()
    print("final: parent exit=%s (None=running)" % rc)
    if not a.no_kill:
        if rc is None:
            print("terminating pid", p.pid)
            try:
                p.terminate()
                p.wait(timeout=15)
            except Exception:
                subprocess.run(["taskkill", "/F", "/T", "/PID", str(p.pid)], capture_output=True)
        for name, pid, ppid, cl, path in snapshot():
            if pid and name in WATCH and path and path.lower().startswith(os.path.dirname(a.exe).lower()):
                print("  killing tracked pid %s %s" % (pid, name))
                subprocess.run(["taskkill", "/F", "/T", "/PID", str(pid)], capture_output=True)
    print("done")


if __name__ == "__main__":
    main()
