// DumpVtable.java -- Ghidra headless postScript: find the vtable that contains the
// mode-dispatch method FUN_11340560 (the function whose `this`=EBX is the mode
// manager, [this+0x4c]=current mode id, and which performs the real switch call
// (**(code**)(*this+0x5c))(&id)). If FUN_11340560 is a method of the mode-manager
// class, its address appears as a slot in that class's vtable. Finding that vtable
// base lets the live Frida scanner locate the mode-manager instance by its vptr
// (heap scan for [this]==base), independent of the current mode id.
//
// FC3.dll image base 0x10000000; addresses below are Ghidra addresses in that space.
import ghidra.app.script.GhidraScript;
import ghidra.program.model.listing.*;
import ghidra.program.model.address.*;
import ghidra.program.model.symbol.*;
import ghidra.program.model.mem.*;
import java.util.*;
import java.io.*;

public class DumpVtable extends GhidraScript {
  static final long DISP = 0x113405a0L; // inside FUN_11340560

  boolean isFuncPtr(long v) {
    if (v < 0x10000000L || v > 0x14000000L) return false;
    try {
      return getFunctionAt(toAddr(v)) != null || getFunctionContaining(toAddr(v)) != null;
    } catch (Exception e) { return false; }
  }

  int readInt(Address a) {
    try { return currentProgram.getMemory().getInt(a); }
    catch (Exception e) { return 0; }
  }

  public void run() throws Exception {
    File out = new File("H:\\FarCryCoop\\scratch\\ghidra\\out");
    out.mkdirs();
    PrintWriter w = new PrintWriter(new OutputStreamWriter(
        new FileOutputStream(new File(out, "vtable_mode.txt")), "UTF-8"));

    Address disp = toAddr(DISP);
    Function f = getFunctionContaining(disp);
    w.println("dispatch 0x" + Long.toHexString(DISP) + " -> function " +
        (f != null ? f.getName() + " @ " + f.getEntryPoint() + " body=" + f.getBody() : "<none>"));
    long entry = (f != null) ? f.getEntryPoint().getOffset() : DISP;
    Address entryAddr = toAddr(entry);

    // 1) all references to the function entry; data refs are candidate vtable slots
    List<Reference> refList = new ArrayList<Reference>();
    ReferenceIterator rit = currentProgram.getReferenceManager().getReferencesTo(entryAddr);
    while (rit.hasNext()) refList.add(rit.next());
    Reference[] refs = refList.toArray(new Reference[0]);
    w.println("references to entry 0x" + Long.toHexString(entry) + ": " + refs.length);
    for (Reference ref : refs) {
      w.println("  ref from " + ref.getFromAddress() + " type=" + ref.getReferenceType());
    }

    // 2) collect every DATA reference (candidate vtable slots); brute-scan if none
    List<Address> slots = new ArrayList<Address>();
    for (Reference ref : refs) {
      if (ref.getReferenceType().isData()) slots.add(ref.getFromAddress());
    }
    if (slots.isEmpty()) {
      Memory mem = currentProgram.getMemory();
      for (MemoryBlock b : mem.getBlocks()) {
        if (!b.isInitialized() || !b.isRead()) continue;
        Address s = b.getStart(), e = b.getEnd();
        for (Address a = s; a.compareTo(e) <= 0; a = a.add(4)) {
          try { if (mem.getInt(a) == (int) entry) slots.add(a); } catch (Exception ex) {}
        }
      }
      w.println("brute-scan found " + slots.size() + " slot(s) pointing to entry");
    }
    if (slots.isEmpty()) { w.println("NO vtable slot found for entry " + entryAddr); w.close(); println("DumpVtable: no slot"); return; }

    for (Address slot : slots) {
      w.println("\n===== candidate slot = " + slot + " =====");
      Address base = slot;
      while (isFuncPtr(readInt(base.subtract(4)))) base = base.subtract(4);
      Address end = slot.add(4);
      while (isFuncPtr(readInt(end))) end = end.add(4);
      long nbytes = end.subtract(base);
      w.println("vtable base = " + base + "  end(excl) = " + end + "  bytes=" + nbytes + "  slots=" + (nbytes / 4));
      for (Address a = base; a.compareTo(end) < 0; a = a.add(4)) {
        long v = readInt(a) & 0xffffffffL;
        long off = a.subtract(base);
        String tag = "";
        if (v == entry) tag = " <== FUN_11340560";
        if (off == 0x5c) tag += " [+0x5c SWITCH]";
        if (off == 0x60) tag += " [+0x60]";
        w.println("  +0x" + Long.toHexString(off) + " = 0x" + Long.toHexString(v) + (isFuncPtr(v) ? "" : " (not-func)") + tag);
      }
      long sw = readInt(base.add(0x5c)) & 0xffffffffL;
      w.println("MODE_MANAGER_VTABLE_BASE_GHIDRA = 0x" + Long.toHexString(base.getOffset()) +
          "  (Frida: A(0x" + Long.toHexString(base.getOffset()) + "))" +
          "  +0x5c=0x" + Long.toHexString(sw) + (isFuncPtr(sw) ? " [valid-func]" : " [NOT-a-func: wrong table]"));
    }
    w.close();
    println("DumpVtable: wrote " + new File(out, "vtable_mode.txt").getAbsolutePath());
  }
}
