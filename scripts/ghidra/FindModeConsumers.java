// FindModeConsumers.java -- offline (FC3_106) discovery of code that uses mode-id constants
// and of the mode-manager class identity (vtable xrefs). Session 8b/8c offline path (H4b).
// Goal: (1) every function that loads one of the mode-id immediates as a scalar constant,
//       (2) every xref to the manager vtables (0x1200e5f8 primary, 0x1200e620 secondary).
// Run: analyzeHeadless <projDir> FC3_106 -process FC3.dll -noanalysis \
//   -scriptPath H:\FarCryCoop\scratch\ghidra\scripts -postScript FindModeConsumers.java
import ghidra.app.script.GhidraScript;
import ghidra.program.model.listing.*;
import ghidra.program.model.scalar.Scalar;
import ghidra.program.model.address.Address;
import ghidra.program.model.symbol.*;
import java.util.*;

public class FindModeConsumers extends GhidraScript {
  // mode-id immediates (unsigned 32-bit). lobby 0x63ddbbcb is the id set by IngameToLobby.
  long[] IDS = { 0xab4fc8e2L, 0x43521e6fL, 0x9991daecL, 0x6c2b3868L, 0xf66ffb87L,
                 0x2100ced7L, 0x63ddbbcbL, 0x100e9f44L };
  long[] VTABLES = { 0x1200e5f8L, 0x1200e620L, 0x11f910e8L };

  public void run() throws Exception {
    println("=== FindModeConsumers " + currentProgram.getName() + " ===");

    // (1) functions that load a mode-id immediate as a constant
    Map<String, Set<Long>> hits = new TreeMap<String, Set<Long>>(); // "0xaddr name" -> ids
    FunctionManager fm = currentProgram.getFunctionManager();
    FunctionIterator fi = fm.getFunctions(true);
    int fnCount = 0, matchFns = 0;
    while (fi.hasNext()) {
      Function fn = fi.next(); fnCount++;
      Set<Long> mine = null;
      InstructionIterator ii = currentProgram.getListing().getInstructions(fn.getBody(), true);
      int ins = 0;
      while (ii.hasNext()) {
        Instruction in = ii.next(); ins++;
        for (int k = 0; k < in.getNumOperands(); k++) {
          for (Object o : in.getOpObjects(k)) {
            if (o instanceof Scalar) {
              long v = ((Scalar) o).getUnsignedValue();
              for (long id : IDS) {
                if (v == id) { if (mine == null) mine = new TreeSet<Long>(); mine.add(id); }
              }
            }
          }
        }
      }
      if (mine != null) {
        hits.put(fn.getEntryPoint() + " " + fn.getName(), mine);
        matchFns++;
        if (matchFns >= 80) { println("  ... (>80 matching functions, truncating list)"); break; }
      }
    }
    println("-- functions loading a mode-id constant (of " + fnCount + " funcs, " + matchFns + " match) --");
    for (Map.Entry<String, Set<Long>> e : hits.entrySet()) {
      StringBuilder sb = new StringBuilder();
      for (long id : e.getValue()) sb.append(String.format("%08X ", id));
      println("  " + e.getKey() + "  ids=[" + sb.toString().trim() + "]");
    }

    // (2) xrefs to the manager vtables
    for (long vt : VTABLES) {
      println("-- xrefs to vtable 0x" + Long.toHexString(vt) + " --");
      ReferenceIterator it = currentProgram.getReferenceManager().getReferencesTo(toAddr(vt));
      int n = 0; boolean any = false;
      while (it.hasNext()) {
        Reference r = it.next(); any = true;
        Function f = getFunctionContaining(r.getFromAddress());
        println(String.format("  from %s type=%s in %s", r.getFromAddress(), r.getReferenceType(),
            f != null ? (f.getEntryPoint() + " " + f.getName()) : "(data/no func)"));
        n++; if (n >= 40) { println("  ... (>40)"); break; }
      }
      if (!any) println("  (none)");
    }
    println("=== done ===");
  }
}
