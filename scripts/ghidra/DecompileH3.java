// DecompileH3.java — Ghidra headless postScript: export pseudocode for the FC3 co-op
// H3 targets from the already-analyzed FC3_106 project (no re-analysis).
// Targets are 1.06 RVAs (FC3.dll image base 0x10000000); see NOTES.md:2176-2258.
import ghidra.app.script.GhidraScript;
import ghidra.app.decompiler.*;
import ghidra.program.model.listing.*;
import ghidra.program.model.address.*;
import java.io.*;

public class DecompileH3 extends GhidraScript {
  public void run() throws Exception {
    long[] targets = {
      0x11279910L, 0x11279a2bL, // co-op-id installer (thiscall)
      0x1127a0f0L, 0x11279fc0L, // the two static callers of the installer
      0x103d1640L,             // CFCXPlaylistService singleton getter
      0x11fab710L,             // PrivateCoopPlaylist ctor/vtable
      0x113405a0L,             // mode dispatch (mov eax,[ebx+0x4c] cmp-chain)
      0x11277c20L, 0x11278160L // playlist-service slots that call the installer
    };
    DecompInterface dc = new DecompInterface();
    dc.openProgram(currentProgram);
    File out = new File("H:\\FarCryCoop\\scratch\\ghidra\\out");
    out.mkdirs();
    PrintWriter w = new PrintWriter(new OutputStreamWriter(new FileOutputStream(new File(out, "decomp_H3.txt")), "UTF-8"));
    for (int i = 0; i < targets.length; i++) {
      long a = targets[i];
      Address addr = toAddr(a);
      Function f = getFunctionAt(addr);
      if (f == null) f = getFunctionContaining(addr);
      w.println("==== target 0x" + Long.toHexString(a) + " ====");
      if (f == null) { w.println("(no function at/containing)"); w.println(); continue; }
      w.println("function @ " + f.getEntryPoint() + "  name=" + f.getName() + "  body=" + f.getBody());
      DecompileResults r = dc.decompileFunction(f, 0, monitor); // timeout 0 = none
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
    println("DecompileH3: wrote " + new File(out, "decomp_H3.txt").getAbsolutePath());
  }
}
