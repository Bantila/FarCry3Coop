// DecompileCore.java -- session 8e (offline H4b continuation).
// Decompile the mode-transition core FUN_11340d00 and the co-op availability predicate
// FUN_1011cb30, plus list xrefs (who calls them) to judge an offline bypass.
import ghidra.app.script.GhidraScript;
import ghidra.app.decompiler.*;
import ghidra.program.model.listing.Function;
import ghidra.program.model.symbol.*;

public class DecompileCore extends GhidraScript {
  long[] T = { 0x117872f0L, 0x103a2d50L, 0x11788030L, 0x10003f00L };
  public void run() throws Exception {
    for (long a : T) {
      println("\n==== target 0x" + Long.toHexString(a) + " ====");
      Function f = getFunctionAt(toAddr(a));
      if (f == null) { println("  no function at 0x" + Long.toHexString(a)); continue; }
      println("  name=" + f.getName() + " body=" + f.getBody() + " sig=" + f.getSignature());
      println("  -- callers/xrefs --");
      ReferenceIterator it = currentProgram.getReferenceManager().getReferencesTo(toAddr(a));
      int n = 0; boolean any=false;
      while (it.hasNext()) {
        Reference r = it.next(); any=true;
        Function cf = getFunctionContaining(r.getFromAddress());
        println("    from " + r.getFromAddress() + " type=" + r.getReferenceType() +
                " in " + (cf != null ? (cf.getEntryPoint() + " " + cf.getName()) : "(data)"));
        n++; if (n >= 30) { println("    ...(>30)"); break; }
      }
      if (!any) println("    (none)");
      DecompInterface d = new DecompInterface();
      d.openProgram(currentProgram);
      DecompileResults r = d.decompileFunction(f, 120, monitor);
      if (r.decompileCompleted()) println(r.getDecompiledFunction().getC());
      else println("  DECOMPILE FAILED: " + r.getErrorMessage());
      d.dispose();
    }
    println("\n=== done ===");
  }
}
