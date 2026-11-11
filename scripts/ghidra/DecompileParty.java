// DecompileParty.java - Ghidra headless postScript: export authoritative pseudocode for the
// Rv party/roster controller on the already-analyzed FC3_106 project (no re-analysis).
// Targets are 1.06 RVAs (FC3.dll base 0x10000000); grounds Sessions 28d-28f.
import ghidra.app.script.GhidraScript;
import ghidra.app.decompiler.*;
import ghidra.program.model.listing.*;
import ghidra.program.model.address.*;
import java.io.*;

public class DecompileParty extends GhidraScript {
  public void run() throws Exception {
    long[] targets = {
      0x11273650L,   // trusted member list walker
      0x11218480L,   // join gate (virtual, ret 0x14)
      0x103660e0L,   // member query (singleton 0x12854784)
      0x1127422aL,   // roster emptiness predicate caller
      0x10070590L,   // member std::map getter (key lo/hi +0x10/+0x14)
      0x1006f990L,   // Session-22 "host test" (looks like a stub here) - confirm
      0x117896a0L,   // called by join gate
      0x10116890L    // controller container release
    };
    DecompInterface dc = new DecompInterface();
    dc.openProgram(currentProgram);
    File out = new File("H:\\FarCryCoop\\scratch\\ghidra\\out");
    out.mkdirs();
    PrintWriter w = new PrintWriter(new OutputStreamWriter(new FileOutputStream(new File(out, "decomp_party.txt")), "UTF-8"));
    for (int i = 0; i < targets.length; i++) {
      long a = targets[i];
      Address addr = toAddr(a);
      Function f = getFunctionAt(addr);
      if (f == null) f = getFunctionContaining(addr);
      w.println("==== target 0x" + Long.toHexString(a) + " ====");
      if (f == null) { w.println("(no function at/containing)"); w.println(); continue; }
      w.println("function @ " + f.getEntryPoint() + "  name=" + f.getName() + "  body=" + f.getBody());
      DecompileResults r = dc.decompileFunction(f, 0, monitor);
      if (r != null && r.decompileCompleted()) {
        w.println(r.getDecompiledFunction().getC());
      } else {
        w.println("decompile FAILED: " + (r != null ? r.getErrorMessage() : "null result"));
      }
      w.println();
      monitor.checkCanceled();
    }
    w.close();
    dc.dispose();
    println("DecompileParty: wrote " + new File(out, "decomp_party.txt").getAbsolutePath());
  }
}
