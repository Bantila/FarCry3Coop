# H7a: offline co-op map selector patch for Far Cry 3 1.05 FC3.dll.
#
# Changes the co-op startup world string "mpdlc1_aegir" -> "fc3_main" so a co-op
# session loads the single-player campaign world instead of the stock co-op island.
# Same single change the community mod OpenWorld220 makes (verified same file offset).
#
# Usage:  python -I H:\FarCryCoop\scratch\h7a_coopmap_patch.py [status|apply|restore]
#   status  - report current state (read-only)
#   apply   - back up FC3.dll (if not already) and write the patch
#   restore - put the un-patched mpdlc1_aegir back
#
# Only touches the 1.05 working copy at H:\FarCryCoop\TestFC3_105. Never the real install.
import os, sys, hashlib, shutil, struct, time

DLL   = r"H:\FarCryCoop\TestFC3_105\bin\FC3.dll"
BAK   = r"H:\FarCryCoop\TestFC3_105\bin\FC3.dll.bak_h7a"
OFFSET = 0x15345D0
OLD = b"mpdlc1_aegir"                 # 12 bytes, null-terminated in the following 6 bytes
NEW = b"fc3_main\x00\x00\x00\x00"     # 12 bytes, same field width, cleanly null-terminated

def out(s): sys.stdout.buffer.write((str(s)+"\n").encode("utf-8","replace")); sys.stdout.flush()
def md5(p):
    h=hashlib.md5()
    with open(p,"rb") as f:
        for b in iter(lambda: f.read(1<<20), b""): h.update(b)
    return h.hexdigest()

def field():
    with open(DLL,"rb") as f:
        f.seek(OFFSET); return f.read(len(OLD))

def kill_game():
    import subprocess
    for im in ("farcry3.exe","farcry3_d3d11.exe"):
        subprocess.run(["taskkill","/IM",im,"/F","/T"],capture_output=True)
    time.sleep(2)

def status():
    if not os.path.exists(DLL): out("MISSING "+DLL); return
    cur=field()
    out("DLL      = %s"%DLL)
    out("size/md5 = %d  %s"%(os.path.getsize(DLL), md5(DLL)))
    out("field @0x%X = %r"%(OFFSET, cur))
    if cur==OLD: out("STATE: UNPATCHED (mpdlc1_aegir -> stock co-op island)")
    elif cur==NEW: out("STATE: PATCHED (fc3_main -> campaign world)")
    else: out("STATE: UNKNOWN field - do NOT patch blindly")
    out("backup   = %s exists=%s"%(BAK, os.path.exists(BAK)))

def apply_patch():
    cur=field()
    if cur==NEW: out("already patched, nothing to do"); return
    if cur!=OLD: out("ABORT: field at 0x%X is %r, expected %r"%(OFFSET,cur,OLD)); return
    kill_game()
    if not os.path.exists(BAK):
        shutil.copy2(DLL,BAK); out("backed up -> %s (md5 %s)"%(BAK, md5(BAK)))
    else:
        out("backup already present: %s"%BAK)
    with open(DLL,"r+b") as f:
        f.seek(OFFSET); f.write(NEW)
    after=field()
    ok = after==NEW
    out("patched: %r -> %r  %s"%(OLD, after, "OK" if ok else "FAILED"))
    out("new md5 = %s"%md5(DLL))
    out("Rollback: python -I %s restore"%os.path.basename(__file__))

def restore():
    cur=field()
    if cur==OLD: out("already unpatched"); return
    kill_game()
    if os.path.exists(BAK):
        shutil.copy2(BAK,DLL); out("restored FC3.dll from %s"%BAK)
    else:
        with open(DLL,"r+b") as f:
            f.seek(OFFSET); f.write(OLD)
        out("re-wrote mpdlc1_aegir in place (no backup present)")
    out("field now = %r  md5=%s"%(field(), md5(DLL)))

if __name__=="__main__":
    cmd=sys.argv[1] if len(sys.argv)>1 else "status"
    {"status":status,"apply":apply_patch,"restore":restore}.get(cmd,status)()
