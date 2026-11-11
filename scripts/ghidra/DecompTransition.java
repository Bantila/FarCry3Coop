// DecompTransition.java -- CALL xrefs to the loader FUN_113409d0, the enqueue
// FUN_11340d00, and the vtable+0x0C handler FUN_10fa1990. Mirrors proven DumpCallers.
import ghidra.app.script.GhidraScript;
import ghidra.program.model.symbol.Reference;
import ghidra.program.model.symbol.ReferenceIterator;
import ghidra.program.model.symbol.RefType;
import ghidra.program.model.listing.Function;
import java.util.List;
import java.util.ArrayList;

public class DecompTransition extends GhidraScript {
  long[] targets = { 0x113409d0L, 0x11340d00L, 0x10fa1990L };
  public void run() throws Exception {
    println("=== DecompTransition " + currentProgram.getName() + " ===");
    for (long t : targets) {
      println("---- callers of 0x" + Long.toHexString(t) + " ----");
      Function fn = getFunctionAt(toAddr(t));
      ReferenceIterator it = currentProgram.getReferenceManager().getReferencesTo(toAddr(t));
      List<Reference> refs = new ArrayList<Reference>();
      while (it.hasNext()) refs.add(it.next());
      int n = 0, calls = 0;
      for (Reference r : refs) {
        RefType rt = r.getReferenceType();
        String tag = (rt.isCall() ? "CALL" : (rt.isData() ? "DATA" : (rt.isComputed() ? "COMPUTED" : "OTHER")));
        if (rt.isCall()) {
          Function caller = currentProgram.getFunctionManager().getFunctionContaining(r.getFromAddress());
          tag = "CALL from " + (caller != null ? (caller.getName() + " @" + caller.getEntryPoint()) : "?");
          calls++;
        }
        println(String.format("  [%s] from %s (%s) via %s", tag, r.getFromAddress(),
            fn != null ? fn.getName() : "FUN_?", rt.toString()));
        n++; if (n >= 60) { println("  ... (>60, truncated)"); break; }
      }
      if (calls == 0) println("  (no direct CALL xrefs -> invoked via vtable slot / indirect)");
      if (refs.isEmpty()) println("  (none at all)");
    }
    println("=== done ===");
  }
}
