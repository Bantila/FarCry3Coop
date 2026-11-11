# Run a Ghidra postScript against the already-analyzed FC3_106 project (no re-analysis).
# Usage: python -I H:\FarCryCoop\scratch\ghidra\scripts\run_headless.py <Script.java> [logfile]
import subprocess, os, sys
script = sys.argv[1]
logf = sys.argv[2] if len(sys.argv) > 2 else "H:\\FarCryCoop\\scratch\\ghidra\\gh_run.log"
env = dict(os.environ)
env["GHIDRA_HOME"] = r"C:\tools\ghidra_12.1.4_PUBLIC"
env["JAVA_HOME"] = r"C:\tools\jdk-21.0.13+9"
env["JAVA_TOOL_OPTIONS"] = "-Xmx6g -Djava.io.tmpdir=H:\\FarCryCoop\\scratch\\ghidra\\tmp"
ah = r"C:\tools\ghidra_12.1.4_PUBLIC\support\analyzeHeadless.bat"
proj = r"H:\FarCryCoop\scratch\ghidra\proj"
scr = r"H:\FarCryCoop\scratch\ghidra\scripts"
for lk in ["FC3_106.lock", "FC3_106.lock~"]:
    p = os.path.join(proj, lk)
    if os.path.exists(p):
        try: os.remove(p)
        except OSError: pass
args = [ah, proj, "FC3_106", "-process", "FC3.dll", "-noanalysis",
        "-scriptPath", scr, "-postScript", script]
r = subprocess.run(args, capture_output=True, text=True, timeout=540, env=env)
out = (r.stdout or "") + "\n===STDERR===\n" + (r.stderr or "")
open(logf, "w", encoding="utf-8").write(out)
print("RC", r.returncode, "len", len(out), "log", logf)
