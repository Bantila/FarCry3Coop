// DecompileGate.java - Ghidra headless postScript: decompile the four FUN_11218480 gate sub-conditions
// + party-service getter, to connect the uplay_proxy loader gate-fakes to the game-level party gate.
// FC3_106 already-analyzed (1.06 RVAs, base 0x10000000). Session 28g follow-up.
import ghidra.app.script.GhidraScript;
import ghidra.app.decompiler.*;
import ghidra.program.model.listing.*;
import ghidra.program.model.address.*;
import java.io.*;

public class DecompileGate extends GhidraScript {
  public void run() throws Exception {
    long[] targets = {
      0x102000d0L,   // online/connected check  FUN_102000d0(mgr, mgr+0x118, mgr+0x11c)
      0x11216750L,   // negative blocker 1 (must be 0)
      0x112166f0L,   // negative blocker 2 (must be 0)
      0x11216690L,   // negative blocker 3 (must be 0)
      0x103660e0L,   // party-service getter (must be != 0)
      0x112734a0L,   // empty-roster (solo) path helper
    };
    DecompInterface dc = new DecompInterface();
    dc.openProgram(currentProgram);
    File out = new File("H:\\FarCryCoop\\scratch\\ghidra\\out");
    out.mkdirs();
    PrintWriter w = new PrintWriter(new OutputStreamWriter(new FileOutputStream(new File(out, "decomp_gate.txt")), "UTF-8"));
    for (int i = 0; i < targets.length; i++) {
      long a = targets[i];
      Address addr = toAddr(a);
      Function f = getFunctionAt(addr);
      if (f == null) f = getFunctionContaining(addr);
      w.println("==== target 0x" + Long.toHexString(a) + " ====");
      if (f == null) { w.println("(no function)"); w.println(); continue; }
      w.println("function @ " + f.getEntryPoint() + "  name=" + f.getName() + "  body=" + f.getBody());
      DecompileResults r = dc.decompileFunction(f, 0, monitor);
      w.println((r != null && r.decompileCompleted()) ? r.getDecompiledFunction().getC()
              : ("decompile FAILED: " + (r != null ? r.getErrorMessage() : "null")));
      w.println();
      monitor.checkCanceled();
    }
    w.close();
    dc.dispose();
    println("DecompileGate: wrote " + new File(out, "decomp_gate.txt").getAbsolutePath());
  }
}
