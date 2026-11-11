// DumpCallers.java -- list CALL xrefs to the mode-dispatcher entry points.
// Run: analyzeHeadless <projDir> FC3_106 -process FC3.dll -noanalysis \
//   -scriptPath H:\FarCryCoop\scratch\ghidra\scripts -postScript DumpCallers.java
import ghidra.app.script.GhidraScript;
import ghidra.program.model.symbol.Reference;
import ghidra.program.model.symbol.ReferenceIterator;
import ghidra.program.model.symbol.RefType;
import ghidra.program.model.listing.Function;
import java.util.List;
import java.util.ArrayList;

public class DumpCallers extends GhidraScript {
  long[] targets = { 0x11340560L, 0x113405a0L };
  public void run() throws Exception {
    println("=== DumpCallers " + currentProgram.getName() + " ===");
    for (long t : targets) {
      println("---- callers of 0x" + Long.toHexString(t) + " ----");
      Function fn = getFunctionAt(toAddr(t));
      List<Reference> refs = new ArrayList<Reference>();
      ReferenceIterator it = currentProgram.getReferenceManager().getReferencesTo(toAddr(t));
      while (it.hasNext()) refs.add(it.next());
      int n = 0;
      for (Reference r : refs) {
        RefType rt = r.getReferenceType();
        String tag = (rt.isCall() ? "CALL" : (rt.isData() ? "DATA" : (rt.isComputed() ? "COMPUTED" : "OTHER")));
        println(String.format("  [%s] from %s (%s) via %s", tag, r.getFromAddress(),
            fn != null ? fn.getName() : "FUN_11340560", rt.toString()));
        n++; if (n >= 60) { println("  ... (>60, truncated)"); break; }
      }
      if (refs.isEmpty()) println("  (none)");
    }
    println("=== done ===");
  }
}
