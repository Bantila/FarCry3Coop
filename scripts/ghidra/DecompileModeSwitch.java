// DecompileModeSwitch.java -- decompile the REAL mode-switch virtual and the dispatcher's
// entry bookkeeping, discovered from the live [MODEPROBE] (session 8b).
// Primary vtable of the live mode-manager = 0x1200e5f8 (Ghidra space). Slots (runtime-probed):
//   +0x20 -> 0x1133fb30   (dispatcher calls (**(code**)(*param_1+0x20))() at entry)
//   +0x38 -> 0x10c471b0
//   +0x5c -> 0x1030f8a0   <-- THE switch virtual: dispatcher calls vtable[+0x5c](&destId)
//   +0x60 -> 0x11340560   (the dispatcher FUN_11340560 itself; secondary table at +0x28)
// Run: analyzeHeadless <projDir> FC3_106 -process FC3.dll -noanalysis \
//   -scriptPath H:\FarCryCoop\scratch\ghidra\scripts -postScript DecompileModeSwitch.java
import ghidra.app.script.GhidraScript;
import ghidra.app.decompiler.DecompInterface;
import ghidra.app.decompiler.DecompileResults;
import ghidra.program.model.listing.Function;

public class DecompileModeSwitch extends GhidraScript {
  long[] targets = { 0x1030f8a0L, 0x1133fb30L, 0x10c471b0L, 0x1200e5f8L };
  public void run() throws Exception {
    DecompInterface decomp = new DecompInterface();
    decomp.openProgram(currentProgram);
    for (long t : targets) {
      Function fn = getFunctionAt(toAddr(t));
      String name = (fn != null) ? fn.getName() : ("@0x" + Long.toHexString(t));
      println("\n\n================= 0x" + Long.toHexString(t) + "  " + name + " =================");
      if (fn == null) { println("  (no function here - maybe data/vtable)"); continue; }
      DecompileResults res = decomp.decompileFunction(fn, 60, monitor);
      if (res != null && res.decompileCompleted()) {
        println(res.getDecompiledFunction().getC());
      } else {
        println("  decompile failed: " + (res != null ? res.getErrorMessage() : "null"));
      }
    }
    decomp.dispose();
  }
}
