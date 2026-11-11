#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""fc3_coop_launch.py - launch two FC3 1.05 instances (the working co-op-boot
build) for the offline loopback co-op probe (PLAN S1).

This does NOT modify the game. It only starts two game processes with separate
saved-settings / user dirs where possible, so two instances can coexist, and
prints the command line to try the engine's own LAN/loopback + `-client -ip`
path once the offline-host detour exists.

Two-instance coexistence on FC3 is the open practical problem: the game locks a
single Uplay/local profile. `--profile <name>` style separation does not exist
for FC3, so this script currently supports ONE instance and DOCUMENTS the
separation options for the owner to decide (copy install vs VM vs the 1.05 mod's
own session flag). See print at the end.

Usage:
  python -I scripts/fc3_coop_launch.py host   # instance A: host a session
  python -I scripts/fc3_coop_launch.py join   # instance B: join 127.0.0.1
  python -I scripts/fc3_coop_launch.py --dry   # print resolved commands only
"""
import os
import sys
import subprocess

# Working co-op-boot 1.05 copy (golden rule 2: never touch H:\Uplay).
GAME_DIR = r"H:\FarCryCoop\TestFC3_105\bin"
EXE = "farcry3_d3d11.exe"  # DX9 exe is the one with the working co-op-boot mod (see NOTES).

# Engine CLI tokens confirmed in FC3_106 InitDuniaEngine @ 0x117a5750 (see NOTES).
HOST_ARGS = ["-coop", "-offline"]
JOIN_ARGS = ["-coop", "-client", "-login", "guest", "-ip", "127.0.0.1"]

def main():
    dry = "--dry" in sys.argv
    mode = next((a for a in sys.argv[1:] if a in ("host", "join")), None)
    exe = os.path.join(GAME_DIR, EXE)
    if mode == "host":
        args = HOST_ARGS
    elif mode == "join":
        args = JOIN_ARGS
    else:
        print(__doc__)
        return
    cmd = [exe] + args
    print("would run:", " ".join(cmd))
    print("cwd     :", GAME_DIR)
    if dry:
        return
    if not os.path.exists(exe):
        print("EXE MISSING:", exe)
        return
    # single-instance note
    print("\nNOTE: FC3 uses one Uplay/local profile lock; a real 2-instance test")
    print("needs install-level separation (copy install) or the mod's own session")
    print("flag. This launcher is a single-instance scaffold pending that decision.")
    subprocess.Popen(cmd, cwd=GAME_DIR)
    print("launched one instance (mode=%s)." % mode)

if __name__ == "__main__":
    main()
