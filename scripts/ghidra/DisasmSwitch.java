// DisasmSwitch.java — headless postScript: linear disassembly of FUN_11340560 (the mode
// dispatcher) to confirm the ABI of the vtable+0x5c "switch to mode" call (which register
// holds `this`, how the &id argument is passed). Reads the saved FC3_106 analysis only.
import ghidra.app.script.GhidraScript;
import ghidra.program.model.listing.*;
import ghidra.program.model.symbol.FlowType;
import ghidra.program.model.address.*;
import java.io.*;

public class DisasmSwitch extends GhidraScript {
  public void run() throws Exception {
    long start = 0x11340560L;
    Function f = getFunctionAt(toAddr(start));
    File out = new File("H:\\FarCryCoop\\scratch\\ghidra\\out");
    out.mkdirs();
    PrintWriter w = new PrintWriter(new OutputStreamWriter(
        new FileOutputStream(new File(out, "disasm_switch.txt")), "UTF-8"));
    if (f == null) {
      w.println("# no function at 0x" + Long.toHexString(start));
      w.close();
      println("DisasmSwitch: no function found");
      return;
    }
    AddressSetView body = f.getBody();
    w.println("# linear disasm FUN_11340560 " + body);
    InstructionIterator it = currentProgram.getListing().getInstructions(body, true);
    int n = 0;
    while (it.hasNext()) {
      Instruction ins = it.next();
      String line = ins.getAddress() + "\t" + ins.toString();
      FlowType ft = ins.getFlowType();
      if (ft.isCall()) line += "\t<CALL flow=" + ft + ">";
      String s = ins.toString();
      if (s.contains("0x5c") || ft.isIndirect()) line += "\t<<<5c/indirect>>>";
      w.println(line);
      n++;
    }
    w.println("# total instructions: " + n);
    w.close();
    println("DisasmSwitch: wrote " + new File(out, "disasm_switch.txt").getAbsolutePath()
        + " (" + n + " insns)");
  }
}
