#!/usr/bin/env python
"""build_uplay_proxy.py - build 32-bit uplay_r1_loader.dll proxy without shell .bat quirks.

Pulls the MSVC x86 environment from vcvars (via python subprocess of cmd.exe /c),
then runs cl/link directly. Output: src/uplay_proxy/uplay_r1_loader.dll
"""
import os, subprocess, sys, glob

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src", "uplay_proxy")

vsbase = r"C:\Program Files\Microsoft Visual Studio\18"
vc = glob.glob(os.path.join(vsbase, "*", "VC", "Auxiliary", "Build", "vcvars32.bat"))
if not vc:
    print("vcvars32.bat not found"); sys.exit(1)

bat = os.path.abspath(os.path.join(ROOT, "local", "scratch", "_vc_env.bat"))
open(bat, "w", newline="").write('@echo off\r\ncall "%s"\r\nset\r\n' % vc[0])
env_raw = subprocess.run(["cmd.exe", "/c", bat], capture_output=True, text=True).stdout
env = dict(os.environ)
for line in env_raw.splitlines():
    if "=" in line:
        k, _, v = line.partition("=")
        env[k.strip()] = v.rstrip()

vct = env.get("VCToolsInstallDir", "").strip()
cl_c = glob.glob(os.path.join(vct, "bin", "HostX86", "x86", "cl.exe")) + glob.glob(os.path.join(vct, "bin", "Hostx64", "x86", "cl.exe"))
if not cl_c:
    print("NO CL found under", vct); sys.exit(1)
CL = cl_c[0]

os.makedirs(os.path.join(SRC, "obj"), exist_ok=True)
cpp = os.path.join(SRC, "uplay_proxy.cpp")
defp = os.path.join(SRC, "uplay_proxy.def")
out = os.path.join(SRC, "uplay_r1_loader.dll")
obj = os.path.join(SRC, "obj", "uplay_proxy.obj")

r = subprocess.run([CL, "/nologo", "/W3", "/O1", "/MT", "/LD", "/DWIN32",
                    "/Fo:" + obj, cpp, "/Fe:" + out,
                    "/link", "/DEF:" + defp, "/MACHINE:X86"],
                   capture_output=True, text=True, cwd=SRC, env=env)
print(r.stdout[-3000:])
print(r.stderr[-2000:])
print("rc:", r.returncode, "dll:", os.path.exists(out), os.path.getsize(out) if os.path.exists(out) else 0)
