import os, subprocess, sys, glob
vsbase = r"C:\Program Files\Microsoft Visual Studio\18"
vc = glob.glob(os.path.join(vsbase, "*", "VC", "Auxiliary", "Build", "vcvars32.bat"))
if not vc:
    print("vcvars32.bat not found"); sys.exit(1)
here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
bat = os.path.join(here, "local", "scratch", "_vc_env_pt.bat")
CRLF = chr(13) + chr(10)
open(bat, "w", newline="").write("@echo off" + CRLF + 'call "' + vc[0] + '"' + CRLF + "set" + CRLF)
env_raw = subprocess.run(["cmd.exe", "/c", bat], capture_output=True, text=True).stdout
env = dict(os.environ)
for line in env_raw.splitlines():
    if "=" in line:
        k, _, v = line.partition("=")
        env[k.strip()] = v.rstrip()
vct = env.get("VCToolsInstallDir", "").strip()
cl_c = glob.glob(os.path.join(vct, "bin", "HostX86", "x86", "cl.exe")) + \
       glob.glob(os.path.join(vct, "bin", "Hostx64", "x86", "cl.exe"))
if not cl_c:
    print("NO CL found under", vct); sys.exit(1)
CL = cl_c[0]
src = os.path.join(here, "src", "uplay_proxy", "proxytest.c")
out = os.path.join(here, "src", "uplay_proxy", "obj")
os.makedirs(out, exist_ok=True)
r = subprocess.run([CL, "/nologo", "/W3", "/O1", "/MT", "/DWIN32",
                    src, "/Fe:" + os.path.join(out, "proxytest.exe"),
                    "/Fo:" + out + os.sep],
                   capture_output=True, text=True, cwd=out, env=env)
print(r.stdout[-600:])
print(r.stderr[-600:])
p = os.path.join(out, "proxytest.exe")
print("rc:", r.returncode, "exe:", os.path.exists(p), os.path.getsize(p) if os.path.exists(p) else 0)
