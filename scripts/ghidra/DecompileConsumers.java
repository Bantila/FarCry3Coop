// DecompileConsumers.java -- decompile the mode-id consumer / classifier / constructor functions
// found by FindModeConsumers, to judge whether any single function brings up a co-op world offline.
import ghidra.app.script.GhidraScript;
import ghidra.app.decompiler.*;
import ghidra.program.model.listing.Function;

public class DecompileConsumers extends GhidraScript {
  long[] T = { 0x10fa1990L, 0x113409d0L, 0x11204b00L, 0x113401c0L,
               0x10fa1e30L, 0x10fa1eb0L, 0x11279a90L };
  public void run() throws Exception {
    DecompInterface d = new DecompInterface();
    d.openProgram(currentProgram);
    for (long a : T) {
      println("\n==== target 0x" + Long.toHexString(a) + " ====");
      Function f = getFunctionAt(toAddr(a));
      if (f == null) { println("  no function at 0x" + Long.toHexString(a)); continue; }
      println("  name=" + f.getName() + " body=" + f.getBody());
      DecompileResults r = d.decompileFunction(f, 90, monitor);
      if (r.decompileCompleted()) println(r.getDecompiledFunction().getC());
      else println("  DECOMPILE FAILED: " + r.getErrorMessage());
      d.dispose(); d = new DecompInterface(); d.openProgram(currentProgram);
    }
    println("\n=== done ===");
  }
}
