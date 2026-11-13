# -*- coding: utf-8 -*-
# @category Jython
"""decompile_session_callers_106.py - open analyzed FC3_106, decompile the Rv
GameSession create/join param BUILDERS + callers, for offline-join hook-point
identification. Read-only (openProgram + DecompInterface; no create/apply/set).

Reads:  H:\FarCryCoop\scratch\ghidra_projects\FC3_106
Writes: H:\FarCryCoop\scratch\ghidra\out\session106\callers.txt
"""
import os
from ghidra.app.decompiler import DecompInterface
from ghidra.util.task import ConsoleTaskMonitor

# (dir is scratch/ghidra/proj, NOT scratch/ghidra_projects)
OUT  = r"H:\FarCryCoop\scratch\ghidra\out\session106"
if not os.path.isdir(OUT):
    os.makedirs(OUT)
# param singletons (names seen in strings) -> their real builders are the CALLERS,
# which assemble the create/join params and call the Rv GameSession service.
SINGLETONS = {
    "CJoinGameSessionParam":   0x10207af0,
    "CCreateGameSessionParam": 0x10208000,
    "CDeleteGameSessionParam": 0x10207b90,
    "CUpdateGameSessionParam": 0x10208060,
}
fm = currentProgram.getFunctionManager()
de = DecompInterface(); de.openProgram(currentProgram)
mon = ConsoleTaskMonitor()
log = []
for name, addr in SINGLETONS.items():
    sfn = fm.getFunctionAt(toAddr(addr))
    log.append("#################### %s singleton @ 0x%x (%s)" % (name, addr, sfn))
    if sfn is None:
        log.append("<no singleton fn>"); continue
    for call in sfn.getCallingFunctions(mon):
        ca = call.getEntryPoint()
        log.append("\n==== CALLER %s @ %s ====" % (call.getName(), ca))
        r = de.decompileFunction(call, 60, mon)
        log.append(r.getDecompiledFunction().getC() if r.decompiledSuccessfully() else "<decompile fail>")
open(os.path.join(OUT, "callers.txt"), "w").write("\n".join(log))
print("wrote callers.txt (%d bytes)" % os.path.getsize(os.path.join(OUT, "callers.txt")))
