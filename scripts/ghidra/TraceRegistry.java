// TraceRegistry.java -- who owns/feeds the global mode registry DAT_128048c0 (vector of
// mode-descriptor ptrs; each entry: refcount@+0x00, name-string@+0x0C, mode-id@+0x20),
// and the central globals DAT_12804acc / DAT_12804b3c.
import ghidra.app.script.GhidraScript;
import ghidra.program.model.symbol.*;
import ghidra.program.model.listing.*;

public class TraceRegistry extends GhidraScript {
  long[] G = { 0x128048c0L, 0x12804accL, 0x12804b3cL };
  public void run() throws Exception {
    for (long g : G) {
      println("\n-- references TO global 0x" + Long.toHexString(g) + " --");
      ReferenceIterator it = currentProgram.getReferenceManager().getReferencesTo(toAddr(g));
      int n = 0;
      while (it.hasNext() && n < 60) {
        Reference r = it.next();
        Function f = getFunctionContaining(r.getFromAddress());
        println("  from " + r.getFromAddress() + " " + r.getReferenceType() +
                " in " + (f != null ? f.getEntryPoint() + " " + f.getName() : "(data)"));
        n++;
      }
      if (n == 0) println("  (none)");
    }
    println("\n=== done ===");
  }
}
