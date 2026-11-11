#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
fc3_h3_run.py - one-command launcher for the H3 live test against a running Far Cry 3.

Wraps scripts/fc3_h3_trace.js in a Python driver so the whole session is captured
to a log file (frida's own REPL + a pipe to a file is fragile because prompt-toolkit
does not like a redirected stdout). This driver:
  * finds the running game process (farcry3.exe / farcry3_d3d11.exe) and attaches,
  * loads fc3_h3_trace.js,
  * mirrors every script console.log/send/error to the console AND to h3_live.log,
  * offers a small command loop (dump / mode / switch dry|go / pop dry|go) that maps
    to the script's rpc.exports, logging each result.

The dangerous RPC levers (switchCoop/populate live calls) require an explicit "go".
Run OFFLINE only; working copy only. See docs/h3-live-test.md (+ .ru.md).

Usage:
  python scripts/fc3_h3_run.py            # auto-detect the FC3 game process
  python scripts/fc3_h3_run.py --pid 1234 # attach to a specific pid
"""
import argparse
import datetime
import json
import os
import sys
import time

try:
    import frida
except ImportError:
    sys.stderr.write("frida is not installed. Run: python -m pip install frida-tools\n")
    sys.exit(1)

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT_JS = os.path.join(HERE, "fc3_h3_trace.js")
LOG_DIR = r"H:\FarCryCoop\scratch"
LOG_PATH = os.path.join(LOG_DIR, "h3_live.log")
# Process image names the game can run as (the DLL is FC3.dll, but the EXE is farcry3*).
GAME_PROCS = ("farcry3", "farcry3_d3d11")


def ts():
    return datetime.datetime.now().strftime("%H:%M:%S.%f")[:-3]


class Logger:
    def __init__(self, path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        backup = None
        rotate_note = None
        if os.path.exists(path):
            stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            backup = path + "." + stamp + ".bak"
            try:
                os.replace(path, backup)
            except OSError as exc:
                # Another launcher instance holds the log open: do not crash, append instead.
                rotate_note = "(could not rotate locked log: %s; appending)" % exc.__class__.__name__
                backup = None
        self.f = open(path, "a", encoding="utf-8", newline="\n")
        self.echo("=== fc3_h3_run session %s ===" % datetime.datetime.now().isoformat(timespec="seconds"))
        self.echo("log file: %s" % path)
        if backup:
            self.echo("(previous log saved to %s)" % backup)
        elif rotate_note:
            self.echo(rotate_note)

    def echo(self, line):
        # print tolerates the cp1251 console; file is utf-8.
        try:
            print(line, flush=True)
        except UnicodeEncodeError:
            sys.stdout.buffer.write((line + "\n").encode("utf-8", "replace"))
            sys.stdout.flush()
        self.f.write(line + "\n")
        self.f.flush()

    def close(self):
        try:
            self.f.close()
        except Exception:
            pass


def find_game_pid(device, log):
    procs = device.enumerate_processes()
    hits = [p for p in procs if p.name and p.name.lower().rsplit(".", 1)[0] in GAME_PROCS]
    if not hits:
        log.echo("No FC3 game process found (looked for: %s)." % ", ".join(GAME_PROCS))
        log.echo("Launch H:\\FarCryCoop\\TestFC3\\bin\\farcry3.exe OFFLINE to the main menu, wait until you")
        log.echo("ARE at the main menu, then re-run. If the game IS running but still not found:")
        log.echo("  - it may be launched as Administrator: a non-elevated Python/Frida cannot see or")
        log.echo("    attach an elevated process. Launch the game WITHOUT 'Run as administrator', or run")
        log.echo("    this launcher from an elevated shell.")
        log.echo("  - to see every process Frida can actually see, run: fc3_h3_run.bat --list")
        log.echo("Or pass the pid explicitly: python scripts/fc3_h3_run.py --pid <pid>")
        return None
    for p in hits:
        log.echo("found game process: pid=%d name=%s" % (p.pid, p.name))
    # Our 1.06 addresses are for the DX9 build (FC3.dll). The DX11 build runs as
    # farcry3_d3d11.exe and loads FC3_d3d11.dll, a different binary we have NOT mapped.
    base_names = [p.name.lower().rsplit(".", 1)[0] for p in hits]
    dx9 = [p for p, bn in zip(hits, base_names) if bn == "farcry3"]
    dx11 = [p for p, bn in zip(hits, base_names) if bn == "farcry3_d3d11"]
    if dx9:
        if dx11:
            log.echo("Both DX9 (farcry3) and DX11 (farcry3_d3d11) found; attaching to the DX9 one "
                     "because our addresses target FC3.dll. Use --pid to pick the other.")
        return dx9[0].pid
    if dx11:
        log.echo("STOP: only the DX11 build is running (farcry3_d3d11.exe loads FC3_d3d11.dll).")
        log.echo("This tool's addresses are for the DX9 build (FC3.dll), which is NOT loaded here;")
        log.echo("fc3_h3_trace.js refuses to run without FC3.dll on purpose.")
        log.echo("Fix: quit this game and launch the DX9 executable")
        log.echo("  H:\\FarCryCoop\\TestFC3\\bin\\farcry3.exe   (NOT farcry3_d3d11.exe),")
        log.echo("then re-run the launcher. If farcry3.exe still ends up as a d3d11 process, tell me")
        log.echo("and we will force the DX9 path (game setting / launch option).")
        return None
    if len(hits) > 1:
        log.echo("Multiple candidates; attaching to the first. Use --pid to choose another.")
    return hits[0].pid


def to_snake(name):
    return "".join("_" + c.lower() if c.isupper() else c for c in name)


def main():
    ap = argparse.ArgumentParser(description="H3 live-test launcher")
    ap.add_argument("--pid", type=int, default=None, help="attach to this pid instead of auto-detect")
    ap.add_argument("--list", action="store_true", help="list processes Frida can see (diagnose attach) and exit")
    ap.add_argument("--grep", default=None, help="with --list, only names containing this substring")
    ap.add_argument("--watch", type=int, default=0, metavar="SECONDS",
                    help="auto mode: stay attached N seconds, watch for a live mode-manager "
                         "capture (do a Main Menu -> Load/Resume in-game during this), log it, then quit")
    args = ap.parse_args()

    log = Logger(LOG_PATH)
    try:
        device = frida.get_local_device()
        if args.list:
            ps = sorted(device.enumerate_processes(), key=lambda p: (p.name or "").lower())
            log.echo("Frida sees %d processes:" % len(ps))
            for p in ps:
                if args.grep and args.grep.lower() not in (p.name or "").lower():
                    continue
                log.echo("  pid=%d  %s" % (p.pid, p.name))
            return 0
        pid = args.pid or find_game_pid(device, log)
        if pid is None:
            return 2
        log.echo("attaching to pid %d ..." % pid)
        session = device.attach(pid)

        with open(SCRIPT_JS, "r", encoding="utf-8") as fh:
            code = fh.read()
        log.echo("loading %s (%d bytes)" % (os.path.basename(SCRIPT_JS), len(code)))

        def on_message(message, data):
            mtype = message.get("type")
            if mtype == "log":
                lvl = message.get("level", "info")
                log.echo("[script:%s] %s" % (lvl, message.get("payload", "")))
            elif mtype == "send":
                log.echo("[send] %s" % json.dumps(message.get("payload"), ensure_ascii=False))
            elif mtype == "error":
                log.echo("[script-error] %s" % message.get("description", message))
                if message.get("stack"):
                    log.echo("  " + message["stack"].replace("\n", "\n  "))
            else:
                log.echo("[msg] %s" % json.dumps(message, ensure_ascii=False))

        script = session.create_script(code)
        script.on("message", on_message)
        script.load()
        exports = script.exports_sync

        def call(jsname, *cargs):
            snake = to_snake(jsname)
            for n in (snake, jsname):
                if hasattr(exports, n):
                    return getattr(exports, n)(*cargs)
            raise AttributeError("rpc export %s (also tried %s) not found" % (jsname, snake))

        HELP = (
            "commands:\n"
            "  dump                read live playlist-service container  (dumpService)\n"
            "  mode                last mode-manager this + [this+0x4c]  (lastMode)\n"
            "  probe [hex]         read-only dump of a live mode-manager this vtable+slots (+0x20/38/5c/60)\n"
            "  switch dry          H3a dry run (no live call)            (switchCoop true)\n"
            "  switch go           H3a LIVE: write [this+0x4c]+call vtable[+0x5c] (may crash)\n"
            "  pop dry             H3b dry run (show svcInit addr)       (populate true)\n"
            "  pop go              H3b LIVE: call FUN_1127a0f0(service)  (may crash)\n"
            "  modeid <this> <id>  DANGEROUS poke: setModeId(this_hex, id_hex)\n"
            "  coop dry/go [mgr [entry]]  H4b LIVE: call vtable[+0x0C](&id,descriptor) (may crash)\n"
            "  modes               dump global mode-list DAT_128048c0 entries (id@+0x20, name@+0xC)\n"
            "  scanmm              scan memory for the live mode-manager (no transition needed)\n"
            "  scanmmv             scan heap for the mode-manager by its VTABLE pointer (robust)\n"
            "  modevt              auto-find ALL vtables dispatching to the mode switch + live instances\n"
            "  help | quit"
        )
        log.echo(HELP)
        log.echo("First: do `dump`, enter+leave a menu in-game, then `mode` (need a non-null thisPtr),")
        log.echo("then `switch dry`, then `switch go`. Watch the game window AND this log on every 'go'.")

        if args.watch:
            log.echo(">>> WATCH MODE: attached and live. Switch to the game NOW and do a real MODE "
                     "CHANGE (ESC / pause does NOT count). Best: go to the Main Menu, then choose "
                     "Load / Resume a checkpoint and let the world load. Do it now, repeatedly.")
            log.echo(">>> Watching %d seconds; captures are logged as [MODECAP]. <<<" % args.watch)
            t0 = time.time()
            seen = set()
            while time.time() - t0 < args.watch:
                try:
                    r = call("lastMode")
                except Exception as exc:
                    log.echo("[watch] poll error: %r" % (exc,))
                    r = None
                if r and r.get("thisPtr") and str(r.get("thisPtr")) != "0":
                    key = str(r.get("thisPtr"))
                    if key not in seen:
                        seen.add(key)
                        log.echo("[MODECAP] " + json.dumps(r, ensure_ascii=False))
                        # immediately probe the live `this` while we are attached (read-only)
                        try:
                            log.echo("[MODEPROBE] " + json.dumps(call("probeMode", str(r.get("thisPtr"))), ensure_ascii=False))
                        except Exception as exc:
                            log.echo("[MODEPROBE] error: %r" % (exc,))
                time.sleep(1.0)
            log.echo(">>> WATCH DONE. captured mode-manager this: %s <<<"
                     % (", ".join(sorted(seen)) if seen else "NONE - no mode transition fired"))
        while not args.watch:
            try:
                line = input("fc3> ").strip()
            except EOFError:
                break
            if not line:
                continue
            log.echo("fc3> " + line)
            parts = line.split()
            cmd, rest = parts[0].lower(), parts[1:]
            try:
                if cmd in ("dump", "dumpservice"):
                    log.echo(json.dumps(call("dumpService"), ensure_ascii=False))
                elif cmd in ("modes", "dumpmodes", "dmpmodes"):
                    log.echo("reading the global mode-list singleton DAT_128048c0 (entries: id@+0x20, name@+0xC) ...")
                    log.echo(json.dumps(call("dumpModes"), ensure_ascii=False))
                elif cmd in ("coop", "entercoop"):
                    mode = rest[0].lower() if rest else "dry"
                    if mode not in ("dry", "go"):
                        log.echo("use: coop dry [mgr_hex [entry_hex]] | coop go [mgr_hex [entry_hex]]")
                        continue
                    mgr = rest[1] if len(rest) > 1 else None
                    entry = rest[2] if len(rest) > 2 else None
                    if mode == "go":
                        log.echo("LIVE call: modeManager vtable[+0x0C](&CO-OP id, descriptor). May crash.")
                    log.echo(json.dumps(call("coopEnter", mode == "dry", mgr, entry), ensure_ascii=False))
                elif cmd in ("netgate", "ng", "gate"):
                    log.echo(json.dumps(call("netgate"), ensure_ascii=False))
                elif cmd in ("sessions", "sess"):
                    log.echo(json.dumps(call("sessions"), ensure_ascii=False))
                elif cmd in ("mmf", "mmfields", "fields"):
                    log.echo(json.dumps(call("mmFields", rest[0] if rest else None), ensure_ascii=False))
                elif cmd in ("loadcoop", "lc"):
                    mode = rest[0].lower() if rest else "dry"
                    if mode not in ("dry", "go"):
                        log.echo("use: loadcoop dry [mgr [entry]] | loadcoop go [mgr [entry]]")
                        continue
                    mgr = rest[1] if len(rest) > 1 else None
                    entry = rest[2] if len(rest) > 2 else None
                    if mode == "go":
                        log.echo("LIVE call: write this+0x48=CO-OP then loader FUN_113409d0(this,&+0x48,desc,0). May crash.")
                    log.echo(json.dumps(call("loadCoop", mode == "dry", mgr, entry), ensure_ascii=False))
                elif cmd in ("mode", "lastmode"):
                    r = call("lastMode")
                    log.echo(json.dumps(r, ensure_ascii=False))
                elif cmd == "probe":
                    arg = rest[0] if rest else None
                    log.echo(json.dumps(call("probeMode", arg), ensure_ascii=False))
                elif cmd == "switch":
                    if not rest or rest[0].lower() not in ("dry", "go"):
                        log.echo("use: switch dry | switch go")
                        continue
                    dry = rest[0].lower() == "dry"
                    if not dry:
                        log.echo("LIVE call: writing [this+0x4c]=CO-OP and calling modeManager vtable[+0x5c].")
                        log.echo("Watch the game window. A crash here is still useful data.")
                    log.echo(json.dumps(call("switchCoop", dry), ensure_ascii=False))
                elif cmd == "pop":
                    if not rest or rest[0].lower() not in ("dry", "go"):
                        log.echo("use: pop dry | pop go")
                        continue
                    dry = rest[0].lower() == "dry"
                    if not dry:
                        log.echo("LIVE call: FUN_1127a0f0(service) populates the co-op container (may crash).")
                    log.echo(json.dumps(call("populate", dry), ensure_ascii=False))
                elif cmd == "modeid":
                    if len(rest) != 2:
                        log.echo("use: modeid <this_hex> <id_hex>")
                        continue
                    log.echo(json.dumps(call("setModeId", rest[0], int(rest[1], 16)), ensure_ascii=False))
                elif cmd in ("scanmm", "scan", "findmm"):
                    log.echo("scanning writable memory for a live mode-manager (this+0x4c == a known mode id) ...")
                    log.echo(json.dumps(call("scanModeManager"), ensure_ascii=False))
                elif cmd in ("scanmmv", "scanv", "findmmv"):
                    log.echo("scanning heap for a live mode-manager instance by its VTABLE pointer (robust) ...")
                    log.echo(json.dumps(call("scanModeManagerByVtable"), ensure_ascii=False))
                elif cmd in ("modevt", "scanmmv2"):
                    log.echo("auto-discovering every vtable whose slot +0x38 == dispatcher, then live instances ...")
                    log.echo(json.dumps(call("scanModeVtables"), ensure_ascii=False))
                elif cmd in ("help", "?", "h"):
                    log.echo(HELP)
                elif cmd in ("quit", "exit", "q"):
                    break
                else:
                    log.echo("unknown command: %s (type 'help')" % cmd)
            except Exception as exc:  # keep the loop alive; log everything
                log.echo("ERROR: %r" % (exc,))

        log.echo("detaching")
        try:
            script.unload()
        except Exception:
            pass
        try:
            session.detach()
        except Exception:
            pass
    finally:
        log.echo("=== session end %s ===" % datetime.datetime.now().isoformat(timespec="seconds"))
        log.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
