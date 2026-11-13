// TraceDescriptor.java -- identify the param_3 co-op descriptor object.
// (a) xrefs to FUN_10fa1990 (mode-change handler) to see who calls it / its vtable slot,
// (b) full body of FUN_10fa1990 (param_3 usage), FUN_10003f00 (string test),
// (c) xrefs to FUN_11340d00.
import ghidra.app.script.GhidraScript;
import ghidra.app.decompiler.*;
import ghidra.program.model.listing.*;
import ghidra.program.model.symbol.*;

public class TraceDescriptor extends GhidraScript {
  public void run() throws Exception {
    long[] XR = { 0x10fa1990L, 0x11340d00L, 0x113409d0L };
    for (long a : XR) {
      println("\n-- xrefs to 0x" + Long.toHexString(a) + " --");
      ReferenceIterator it = currentProgram.getReferenceManager().getReferencesTo(toAddr(a));
      int n = 0;
      while (it.hasNext() && n < 40) {
        Reference r = it.next();
        Function f = getFunctionContaining(r.getFromAddress());
        println("  from " + r.getFromAddress() + " " + r.getReferenceType() +
                " in " + (f != null ? f.getEntryPoint() + " " + f.getName() : "(data)"));
        n++;
      }
      if (n == 0) println("  (none)");
    }
    DecompInterface d = new DecompInterface();
    d.openProgram(currentProgram);
    long[] BD = { 0x10fa1990L, 0x10003f00L };
    for (long a : BD) {
      println("\n==== body 0x" + Long.toHexString(a) + " ====");
      Function f = getFunctionAt(toAddr(a));
      if (f == null) { println("  none"); continue; }
      DecompileResults r = d.decompileFunction(f, 90, monitor);
      if (r.decompileCompleted()) println(r.getDecompiledFunction().getC());
      else println("  FAIL " + r.getErrorMessage());
      d.dispose(); d = new DecompInterface(); d.openProgram(currentProgram);
    }
    println("\n=== done ===");
  }
}
