// DecompRegistry.java -- decompile the mode-registry init + the runtime populate/bootstrap + a reader.
import ghidra.app.script.GhidraScript;
import ghidra.app.decompiler.*;
import ghidra.program.model.listing.Function;

public class DecompRegistry extends GhidraScript {
  long[] T = { 0x10048230L, 0x11756e00L, 0x11756c50L, 0x100480f0L };
  public void run() throws Exception {
    DecompInterface d = new DecompInterface();
    d.openProgram(currentProgram);
    for (long a : T) {
      println("\n==== target 0x" + Long.toHexString(a) + " ====");
      Function f = getFunctionAt(toAddr(a));
      if (f == null) { println("  none"); continue; }
      println("  sig " + f.getSignature().getName());
      DecompileResults r = d.decompileFunction(f, 90, monitor);
      if (r.decompileCompleted()) println(r.getDecompiledFunction().getC());
      else println("  FAIL " + r.getErrorMessage());
      d.dispose(); d = new DecompInterface(); d.openProgram(currentProgram);
    }
    println("\n=== done ===");
  }
}
