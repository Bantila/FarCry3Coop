# Test whether the Uplay hub forwards HKCU\Software\Ubisoft\Far Cry 3\StartArguments
# into the command line of the game process it spawns.
# It writes a benign value (default '-affinity 2'), launches the stub once, records
# child command lines, then ALWAYS restores the previous registry value.
#
#   python -X utf8 scripts/fc3_test_startargs.py [--value=-affinity 2] [--wait=70]
#   python -X utf8 scripts/fc3_test_startargs.py --restore-only
import argparse
import json
import subprocess
import time
import winreg

HKCU_KEY = r"Software\Ubisoft\Far Cry 3"
VALUE = "StartArguments"
STUB = r"H:/FarCryCoop/TestFC3/bin/farcry3_d3d11.exe"
CANON = "H:\\Uplay\\Far Cry 3"


def read_value():
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, HKCU_KEY, 0, winreg.KEY_READ)
        v, _ = winreg.QueryValueEx(key, VALUE)
        winreg.CloseKey(key)
        return v if v else ""
    except OSError:
        return None


def write_value(text):
    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, HKCU_KEY, 0, winreg.KEY_SET_VALUE)
    winreg.SetValueEx(key, VALUE, 0, winreg.REG_SZ, text)
    winreg.CloseKey(key)


def snapshot():
    cmd = [
        "powershell", "-NoProfile", "-Command",
        "Get-CimInstance Win32_Process | Select-Object Name,ProcessId,"
        "ParentProcessId,CommandLine,ExecutablePath | ConvertTo-Json -Compress",
    ]
    out = subprocess.run(cmd, capture_output=True, text=True).stdout.strip()
    if not out:
        return []
    data = json.loads(out)
    if isinstance(data, dict):
        data = [data]
    return data


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--value", default="-affinity 2")
    p.add_argument("--wait", type=int, default=70)
    p.add_argument("--args", default="-language=Russian")
    p.add_argument("--restore-only", action="store_true")
    a = p.parse_args()

    old = read_value()
    print("HKCU\%s\%s BEFORE = %r" % (HKCU_KEY, VALUE, old))
    if a.restore_only:
        if old:
            write_value("")
        print("restore-only: nothing else done")
        return

    if old is None:
        print("key/value missing -> abort (value not created)")
        return

    try:
        write_value(a.value)
        print("HKCU value set to %r" % a.value)
        proc = subprocess.Popen([STUB] + a.args.split())
        print("launched %s %s pid=%d" % (STUB, a.args, proc.pid))
        seen = {}
        for i in range(a.wait // 5):
            time.sleep(5)
            rows = [r for r in snapshot() if "farcry" in (r.get("Name") or "").lower()]
            for r in rows:
                pid = r.get("ProcessId")
                line = r.get("CommandLine") or ""
                path = r.get("ExecutablePath") or ""
                if path.startswith(CANON):
                    print("[%3ds] CANON pid=%s ppid=%s" % ((i + 1) * 5, pid, r.get("ParentProcessId")))
                    print("      cmd = %s" % line)
                    print("      FORWARDED = %s" % (a.value in line))
                if pid and pid not in seen:
                    seen[pid] = True
            print("[%3ds] farcry processes: %d" % ((i + 1) * 5, len(rows)))
            if any((r.get("CommandLine") or "").startswith('"%s' % CANON) for r in rows):
                break
    finally:
        for pid in list(seen):
            try:
                subprocess.run(["taskkill", "/F", "/T", "/PID", str(pid)],
                               capture_output=True, text=True)
            except Exception:
                pass
        try:
            write_value(old)
            print("RESTORED HKCU\%s\%s = %r" % (HKCU_KEY, VALUE, read_value()))
        except Exception as exc:
            print("RESTORE FAILED: %s" % exc)


if __name__ == "__main__":
    main()
