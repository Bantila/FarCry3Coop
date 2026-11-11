#!/usr/bin/env python
"""fc3_coop_force.py - attach Frida to running Far Cry 3 and run fc3_coop_force.js (direction-B go/no-go).

In-memory only (no disk writes): observes net mode + online-coop entry and can force the RendezVous gate.
Launch FC3 via Ubisoft Connect, reach main menu, run this (it waits for the game), then navigate to co-op.
Writes local/scratch/frida_force_<ts>.log.
"""
import sys, os, time
import frida

PROC = "farcry3_d3d11.exe"
HERE = os.path.dirname(os.path.abspath(__file__))
JS = os.path.join(HERE, "fc3_coop_force.js")
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
OUTDIR = os.path.join(REPO, "local", "scratch")
os.makedirs(OUTDIR, exist_ok=True)
OUT = os.path.join(OUTDIR, "frida_force_%s.log" % time.strftime("%Y%m%d_%H%M%S"))

def wf(line):
    try:
        with open(OUT, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception as e:
        print("[write-error] %s" % e, flush=True)

def on_message(message, data):
    if message.get("type") == "send":
        line = str(message.get("payload"))
    elif message.get("type") == "error":
        line = "[frida-error] " + message.get("description", str(message))
    else:
        line = str(message)
    print(line, flush=True); wf(line)

def on_log(level, text):
    line = "[js-log %s] %s" % (level, text)
    print(line, flush=True); wf(line)

def main():
    devs = frida.enumerate_devices()
    local = next((d for d in devs if d.type == "local"), None)
    if not local:
        print("no local frida device"); return 2

    def find_pid():
        for p in local.enumerate_processes():
            if p.name.lower() == PROC.lower():
                return p.pid
        return None

    wf("START watching for %s -> %s" % (PROC, OUT))
    print("watching for %s; launch it via Ubisoft Connect and reach the main menu. Ctrl+C to stop." % PROC, flush=True)
    session = None; last = None
    for attempt in range(1, 40):
        pid = find_pid()
        if pid is None:
            if attempt == 1:
                print("(%s not running yet) waiting..." % PROC, flush=True)
            time.sleep(3); continue
        try:
            print("attaching to %s pid=%d (attempt %d)..." % (PROC, pid, attempt), flush=True)
            session = frida.attach(pid); wf("ATTACHED pid=%d" % pid); break
        except Exception as e:
            last = e
            print("attach to pid=%d failed: %s (re-resolving in 3s)" % (pid, e), flush=True)
            time.sleep(3)
    if session is None:
        print("could not attach: %s" % last); wf("ATTACH-ABORT %s" % last); return 4
    script = session.create_script(open(JS, encoding="utf-8").read())
    script.on("message", on_message)
    try: script.on("log", on_log)
    except Exception: pass
    script.load()
    print("hooked. In-game: co-op -> connect. Watch [obs]/[FORCE]/[NET]/[DNS]. Ctrl+C to stop.", flush=True)
    wf("LOADED")
    try:
        while True: time.sleep(0.5)
    except KeyboardInterrupt:
        print("detaching"); wf("DETACH")
    return 0

if __name__ == "__main__":
    sys.exit(main())
