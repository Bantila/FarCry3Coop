"""Read-only probe: locate LAN-matchmaking / hosting anchor strings in FC3.dll and the code
that references them. Print RVAs (VA - imageBase). No writes.

Usage: python -I scripts/fc3_lan_probe.py [strings|xrefs] [extra substr ...]
"""
import struct, sys
sys.path.insert(0, r"D:/Projects/Co-op Anything/FarCry3Coop-bantila/scripts")
from fc3_addrmap import PE

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

DLL = r"H:/FarCryCoop/Downloads/patch_solo_offline_coop_vanilla-262/Far Cry 3/bin/FC3.dll"

ANCHORS = [
    "LAN matchmaking discovery on loopback enable",
    "LAN matchmaking socket option SO_REUSEADDR",
    "LAN matchmaking",
    "LanHostBroadcastPort",
    "LanClientBroadcastPort",
    "LanMatchmakingReuseAddress",
    "LanMatchmakingDiscoveryOnLoopbackEnable",
    "lanmanager",
    "MaximumPeerCount",
    "Maximum peers in a network",
    "EnableNatTraversal",
    "CSessionMatchmakingProvider",
    "CGameMatchmakingProvider",
    "CSessionInviteProvider",
    "CGameInviteProvider_RdV",
    "CSessionProvider",
    "CGamePartyProvider_UplayPC",
    "ELoginStatus_LoggedInUplayServicesExecuting",
    "outEvent::SessionMigrationStart",
    "outEvent::SessionMigrationEnd",
    "HostSession",
    "CreateSession",
    "JoinSession",
    "NetEngineType",
]

def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "strings"
    pe = PE(DLL)
    ib = pe.base
    print("imageBase=0x%08x  text=[0x%08x,0x%08x)" % (ib, pe.text[0], pe.text[1]))
    for a in ANCHORS:
        vas = pe.find_cstring(a)
        if not vas:
            # substring search anywhere (not necessarily NUL-terminated start)
            pat = a.encode()
            hits, i = [], pe.d.find(pat)
            while i >= 0 and len(hits) < 8:
                hits.append(pe.off2va(i)); i = pe.d.find(pat, i+1)
            vas = hits
            tag = "SUBSTR"
        else:
            tag = "CSTR"
        print("\n== %s [%s] %d hit(s)" % (a, tag, len(vas)))
        for va in vas:
            print("   str VA=0x%08x RVA=0x%x" % (va, va-ib))
        if mode == "xrefs":
            for va in vas:
                for off in pe.code_refs(va):
                    cva = pe.off2va(off)
                    print("   xref code VA=0x%08x RVA=0x%x" % (cva, cva-ib))

main()
