"""fc3_upc_probe.py — ask Ubisoft Connect to launch OUR 1.06 test copy with quick-launch arguments.

Evidence this test is based on (fc3_launch_probe.py run, 2026-11-02): the DRM stub does not run the game
directly. It hands the command line to Ubisoft Connect:

    upc.exe  -upc_uplay_id 46 -language=Russian -quickstartup -host fc3_main -login coop1 -coop \
             -upc_desktop_mode -upc_game_starter            (pid 18080, canonical install)
    ... and upc then starts   "H:/Uplay/Far Cry 3/bin/farcry3_d3d11.exe" -language=Russian   (args dropped)

So the arguments ARE forwarded to the launcher; the drop happens when upc starts the game without them.
This probe asks upc to launch the test copy instead and checks whether the test copy's game process
appears WITH the quick-launch arguments. It is read-only: it starts processes, watches the process tree,
then terminates what it started. Nothing in any game folder is written.

Usage: python -I tools/fc3_upc_probe.py [--uplay-id 46] [--test-exe PATH] [--args "..."] [--wait 90]
"""
import argparse
import os
import subprocess
import sys
import time
from datetime import datetime

DEFAULT_ARGS = ("-language=Russian -quickstartup -host fc3_main -login coop1 -coop")
WATCH = ("farcry3_d3d11.exe", "FC3.exe", "FC3_d3d11.exe", "FC3Updater.exe", "upc.exe")


def stamp():
    return datetime.now().strftime("%H:%M:%S")


def snapshot():
    """Return {pid: (name, ppid, path, command line)} for the processes we watch."""
    ps = ("Get-CimInstance -ClassName Win32_Process | Where-Object "
          "{$_.Name -match 'farcry3|FC3|upc'} | "
          "Select-Object ProcessId,ParentProcessId,Name,ExecutablePath,CommandLine | "
          "Format-List ProcessId,ParentProcessId,Name,ExecutablePath,CommandLine")
    try:
        out = subprocess.run(["powershell", "-NoProfile", "-Command", ps],
                             capture_output=True, text=True, timeout=60).stdout
    except Exception as exc:
        return {}, "snapshot failed: %s" % exc
    items, res, cur = out.replace("\r", "").split("\n\n"), {}, {}
    for block in items:
        for line in block.split("\n"):
            if ":" in line:
                k, v = line.split(":", 1)
                cur[k.strip()] = v.strip()
        if "ProcessId" in cur:
            try:
                res[int(cur["ProcessId"])] = (cur.get("Name"), int(cur.get("ParentProcessId", 0) or 0),
                                              cur.get("ExecutablePath"), cur.get("CommandLine"))
            except ValueError:
                pass
        cur = {}
    return res, None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--uplay-id", default="46", help="Ubisoft Connect game id to start")
    ap.add_argument("--test-exe", default=r"H:/FarCryCoop/TestFC3/bin/farcry3_d3d11.exe")
    ap.add_argument("--args", default=DEFAULT_ARGS)
    ap.add_argument("--wait", type=int, default=90)
    ap.add_argument("--no-kill", action="store_true")
    a = ap.parse_args()

    upc = os.path.expandvars(r"%ProgramFiles(x86)%\Ubisoft\Ubisoft Game Launcher\upc.exe")
    if not os.path.isfile(upc):
        print("upc.exe not found at %s" % upc)
        return 2

    cmd = [upc, "-upc_uplay_id", a.uplay_id] + a.args.split() + ["-upc_desktop_mode", "-upc_game_starter"]
    print("launch: %s" % " ".join(cmd))
    before, err = snapshot()
    if err:
        print(err)
    print("baseline game pids: %s" % sorted(before))
    p = subprocess.Popen(cmd)
    print("launcher pid=%d" % p.pid)

    seen, started, err = {}, p.pid, None
    t0 = time.time()
    while time.time() - t0 < a.wait:
        time.sleep(6)
        cur, err = snapshot()
        if err:
            print(err)
            continue
        for pid, info in cur.items():
            if pid in before or pid in seen:
                continue
            seen[pid] = info
            name, ppid, path, cl = info
            tag = "OUR COPY" if a.test_exe and path and os.path.normpath(path).lower() == os.path.normpath(a.test_exe).lower() else "other"
            print("  + %4ds NEW %-18s pid=%-6d ppid=%-6d %s" % (int(time.time() - t0), name, pid, ppid, tag))
            print("        path=%s" % path)
            print("        cmd=%s" % cl)
        rc = p.poll()
        if rc is not None:
            print("  + %4ds launcher exited code=%s" % (int(time.time() - t0), rc))
            break

    verdict = [i for i in seen.values() if i[3] and any(t in i[3] for t in ("-host", "-coop", "-quickstartup"))]
    print("\nprocesses with quick-launch args preserved:")
    for name, ppid, path, cl in verdict:
        print("  %s pid? cmd=%s" % (name, cl))
    if not verdict:
        print("  (none)")

    if not a.no_kill:
        for pid, (name, _, _, _) in list(seen.items()):
            if name and name.lower() in WATCH and pid not in before:
                try:
                    subprocess.run(["taskkill", "/T", "/F", "/PID", str(pid)], capture_output=True, timeout=30)
                    print("terminated pid=%d (%s)" % (pid, name))
                except Exception as exc:
                    print("kill %s failed: %s" % (pid, exc))
    print("done")
    return 0


if __name__ == "__main__":
    sys.exit(main())
