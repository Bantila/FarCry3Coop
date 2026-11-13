/*
 * fc3_h3_trace.js — H3 runtime trace for the FC3 co-op mode switch (Frida).
 *
 * Implements the Phase-2 "H3" lead in PLAN.md ("Hook status after session 7"):
 * session-7 decompilation pinned the mechanism. The mode-manager field [this+0x4c]
 * holds the live mode id; the real "switch to mode" call is modeManager->vtable[+0x5c]
 * (inside FUN_11340560); the co-op session lives in the CFCXPlaylistService container
 * [service+0x8c0], populated by FUN_1127a0f0 -> FUN_11279910 (see NOTES.md session 7).
 * This script OBSERVES those at runtime and exposes the two static levers as RPC
 * (switchCoop / populate) for the owner to run against an OFFLINE instance.
 *
 * All addresses below are the 1.06 build (H:\FarCryCoop\TestFC3\bin\FC3.dll,
 * image base 0x10000000). 1.05 is the primary target: re-locate every address
 * with scripts/fc3_addrmap.py before pointing this at a 1.05 process.
 * Anchors verified in NOTES.md:2176-2258 (probes p280-p315).
 *
 * SAFETY: attach only to an OFFLINE game instance (`-offline` debug menu), never
 * to an online / Ubisoft Connect session — frida injection there risks an anti-cheat
 * flag, and the process guard is OpenMutexA("FarCry3Instance"). Read the AGENTS
 * rules: never touch the real install, use the working copy only.
 *
 * Usage (owner's machine, game already running offline):
 *   scripts\fc3_h3_run.bat                            # one-command launcher (auto-detects the game pid,
 *                                                       loads this script, logs to h3_live.log, cmd loop)
 *   frida -n farcry3 -l scripts/fc3_h3_trace.js      # by process name (game is farcry3.exe, NOT FC3)
 *   frida -p <pid> -l scripts/fc3_h3_trace.js      # by pid
 * In the REPL:
 *   rpc.exports.dumpService()      # read the live playlist-service container
 *   rpc.exports.lastMode()         # last mode-manager this + [this+0x4c] seen
 *   rpc.exports.setModeId(addr, id)  # DANGEROUS experimental poke, see below
 *   rpc.exports.switchCoop(true)   # H3a: dryRun first; enter a menu so lastMode() caches `this`
 *   rpc.exports.switchCoop(false)  # H3a: write [this+0x4c]=CO-OP + call vtable[+0x5c] (may crash)
 *   rpc.exports.populate(true)     # H3b: dryRun, show svcInit address
 *   rpc.exports.populate(false)    # H3b: call FUN_1127a0f0(service) to build the co-op entry (may crash)
 */
'use strict';

var MODULE = 'FC3.dll';
var IMAGE_BASE = 0x10000000; // FC3.dll preferred/actual base; A() re-anchors to the real one

// --- 1.06 anchors (NOTES.md session 5-7). Map to 1.05 before use. ---
var ADDR = {
  dispatchMode:  0x113405a0, // cmp-chain inside FUN_11340560 (body 11340560-113409cd); ebx=this, [this+0x4c]=mode id
  modeSwitchVt:  0x5c,        // *(this->vtable+0x5c)(&id) is the real "switch to mode" virtual (FUN_11340560)
  svcInit:       0x1127a0f0, // FUN_1127a0f0(this): builds [svc+0x8c0] container + runs installer; sets +0x488/+0x4b0..
  containerAddVt:0x5c,        // *(svc+0x8c0)->vtable+0x5c(&obj,id,0) = Add a co-op entry into the container
  byKeyLookup:   0x113224e0, // FUN_113224e0(&id): resolve playlist entries by mode-key (used with 0x43521e6f)
  installer:     0x11279910, // co-op-id installer (thiscall, this in ecx); static callers 0x1127a0f0 / 0x11279fc0
  callerA:       0x1127a0f0, // one of the two static callers of the installer (playlist-service method)
  callerB:       0x11279fc0, // the other static caller
  svcSingleton:  0x12863890, // CFCXPlaylistService: the instance is the object AT this addr (guard 1286388c), not a ptr
  svcGetter:     0x103d1640, // singleton getter: returns &DAT_12863890 directly (NOT called here)
  idMaskReg:     0x128048c0, // id -> mask registry global
  netSess:       0x12804acc, // session/netplay manager global; +0x6c byte = 'co-op session available' gate; +0x68 = handle ptr
  loader9d0:     0x113409d0, // FUN_113409d0(this,&this+0x48,descriptor,p4): the actual mode loader; reads id from *(&this+0x48); CO-OP 0x43521e6f is in its branch set
  centralObj:    0x12804acc, // central game object (4529 refs; +0x68 component container)
  installG_a:    0x12891ca0, // diagnostic install-global (NOT the live lever; see H1 demotion)
  installG_b:    0x12891ca8,
  // Mode-manager vtable addresses (Ghidra 0x10000000 space), recovered by DumpVtable.java:
  // both are classes that implement FUN_11340560 (the mode dispatch, slot +0x38); a live
  // instance's vptr == A(mmVtable*), and [instance+0x4c] is the current mode id.
  mmVtable0:     0x1200e5f8, // CONFIRMED live mode-manager PRIMARY vtable (session 8c probeMode); dispatcher at +0x60
  mmVtable1:     0x1200e620, // secondary base subobject at primary+0x28
  mmVtable2:     0x11f910e8, // 16-slot vtable (shares first 5 slots; slot +0x38 = FUN_11340560)
  mmDispatchFn:  0x11340560  // the vtable slot VALUE = function ENTRY (NOT the 0x113405a0 dispatch point)
};

// Co-op mode id + the five sibling mode-hash ids seen in the dispatch chain.
var MODE = {
  coop: 0x43521e6f,
  known: [0xab4fc8e2, 0x43521e6f, 0x9991daec, 0x6c2b3868, 0xf66ffb87, 0x2100ced7]
};

var mod = Process.findModuleByName(MODULE);
if (mod === null) {
  throw new Error(MODULE + ' not loaded; launch the DX9 build (farcry3.exe -> FC3.dll) offline first. '
    + 'The DX11 build (farcry3_d3d11.exe) loads FC3_d3d11.dll, which this tool does NOT target.');
}
var base = mod.base;
function A(va) { return base.add(va - IMAGE_BASE); }

var lastMode = { at: 0, thisPtr: 0, id: 0, idName: '', mmPtr: null };
function nameOf(id) {
  if (id === MODE.coop) return 'CO-OP';
  return '?';
}

// --- Hook 1: the mode dispatch. Reveals the live mode-manager `this` (ebx) and
//     the current mode id [this+0x4c]. This is H3 target #2.
try {
  Interceptor.attach(A(ADDR.dispatchMode), {
    onEnter: function () {
      var ebx = this.context.ebx;
      var id = 0;
      try { id = ebx.add(0x4c).readU32(); } catch (e) {}
      lastMode.at = ADDR.dispatchMode;
      lastMode.thisPtr = ebx.toString();
      lastMode.mmPtr = ebx;
      lastMode.id = id;
      lastMode.idName = nameOf(id);
      console.log('[dispatch] this(ebx)=' + ebx + ' [this+0x4c]=0x' +
        (id >>> 0).toString(16) + ' ' + lastMode.idName);
    }
  });
  console.log('attached dispatch @ ' + A(ADDR.dispatchMode));
} catch (e) { console.log('dispatch hook failed: ' + e); }

// --- Hook 2: the co-op-id installer. Reveals the RUNTIME caller (thiscall this in
//     ecx) and a full backtrace -> H3 target #1 (who sets the live mode / triggers
//     the co-op install). Statically the callers are callerA/callerB.
function installerHook(label) {
  return {
    onEnter: function () {
      var svc = this.context.ecx; // thiscall this (playlist-service object)
      var bt = [];
      try {
        bt = Thread.backtrace(this.context, Backtracer.ACCURATE)
             .map(function (a) {
               var off = a.sub(base); // RVA, comparable to ADDR values
               return a + ' (FC3+0x' + off.toString(16) + ')';
             });
      } catch (e) { bt = ['backtrace failed: ' + e]; }
      var container = 'n/a';
      try { container = svc.add(0x8c0).readPointer() + ' / +' +
        svc.add(0x8c4).readPointer().toString(); } catch (e) {}
      console.log('[' + label + '] installer entered; this(ecx)=' + svc +
        '  [this+0x8c0/+0x8c4]=' + container);
      console.log('  backtrace:\n    ' + bt.join('\n    '));
    }
  };
}
['installer', 'callerA', 'callerB'].forEach(function (k) {
  try {
    Interceptor.attach(A(ADDR[k]), installerHook(k));
    console.log('attached ' + k + ' @ ' + A(ADDR[k]));
  } catch (e) { console.log(k + ' hook failed: ' + e); }
});

// --- Locate the live mode-manager WITHOUT needing the dispatch hook to fire.
// The mode manager holds its current mode id at [this+0x4c]; that id is one of the
// known mode-hash ids. Scan writable memory for any of those ids, treat the
// candidate object start as this = (id_addr - 0x4c), and validate it looks like a
// C++ object: its first qword is a vtable pointer inside FC3.dll, and that vtable's
// first entry is also inside FC3.dll. Returns candidates for inspection; on a hit
// that validates, also caches lastMode.mmPtr so switchCoop() can be used.
function idPattern(u32) {
  var b = [u32 & 0xff, (u32 >>> 8) & 0xff, (u32 >>> 16) & 0xff, (u32 >>> 24) & 0xff];
  return b.map(function (x) { return ('0' + x.toString(16)).slice(-2); }).join(' ');
}
function inModule(p) {
  try { return !p.isNull() && p.compare(base) >= 0 && p.compare(base.add(mod.size)) < 0; }
  catch (e) { return false; }
}
function findModeManagerCore() {
  var ids = MODE.known.concat([0x63ddbbcb]); // + the lobby id the dispatcher remaps to
  // Only the process heap holds the live, constructed mode-manager instance. DLL/EXE
  // image data segments contain the SAME id constants in static tables (false
  // positives). Windows committed heap is sometimes type 'private' and sometimes
  // 'anonymous', so do NOT trust type; instead drop any range that belongs to a
  // loaded module (findModuleByAddress on its base), which removes all image .data.
  var ranges = Process.enumerateRanges({ protection: 'rw-', coalesce: true })
    .filter(function (x) { return Process.findModuleByAddress(x.base) === null; });
  var patList = ids.map(function (id) { return { pat: idPattern(id), id: id }; });
  var scanned = 0, MAXSCAN = 800 * 1024 * 1024;
  var found = [];
  for (var r = 0; r < ranges.length && scanned < MAXSCAN && found.length < 16; r++) {
    var rng = ranges[r];
    scanned += rng.size;
    for (var pi = 0; pi < patList.length && found.length < 16; pi++) {
      var hits = [];
      try { hits = Memory.scanSync(rng.base, rng.size, patList[pi].pat); }
      catch (e) { continue; }
      for (var h = 0; h < hits.length && found.length < 16; h++) {
        var idAddr = hits[h].address;
        var id = patList[pi].id;
        var thisp = idAddr.sub(0x4c);
      var vtable, v0;
      try { vtable = thisp.readPointer(); v0 = vtable.readPointer(); } catch (e) { continue; }
      if (!inModule(vtable) || !inModule(v0)) continue;
      var vt5c = null;
      try { vt5c = vtable.add(ADDR.modeSwitchVt).readPointer(); } catch (e) {}
      found.push({
        this: thisp.toString(), modeId: '0x' + (id >>> 0).toString(16),
        vtable: vtable.toString(), vtableRva: '0x' + vtable.sub(base).toString(16),
        vt5c: vt5c ? vt5c.toString() : null,
        vt5cInModule: vt5c ? inModule(vt5c) : false
      });
      }
    }
  }
  // cache the first candidate whose +0x5c slot is a module function (best switch target)
  var chosen = null;
  for (var c = 0; c < found.length; c++) {
    if (found[c].modeId === '0x43521e6f' && found[c].vt5cInModule) { chosen = found[c]; break; }
  }
  if (!chosen) for (var c2 = 0; c2 < found.length; c2++) {
    if (found[c2].vt5cInModule) { chosen = found[c2]; break; }
  }
  if (!chosen && found.length) chosen = found[0];
  if (chosen) {
    lastMode.mmPtr = ptr(chosen.this);
    lastMode.thisPtr = chosen.this;
    lastMode.id = parseInt(chosen.modeId, 16);
    lastMode.idName = nameOf(lastMode.id);
    lastMode.at = 'scan';
  }
  return { scannedBytes: scanned, ranges: ranges.length, count: found.length, candidates: found,
           cachedForSwitch: chosen ? chosen.this : null };
}

// --- Locate the live mode-manager instance directly by its vtable pointer (robust:
// independent of the current mode id, unlike the id-scan). DumpVtable.java proved
// the mode-manager classes have vtables at ADDR.mmVtable1 / mmVtable2 (Ghidra space),
// and FUN_11340560 (the dispatcher we hook) is slot +0x38 of both. A live object's
// vptr field == A(mmVtable); scan the heap for that pointer value -> real instances;
// [instance+0x4c] is the current mode id. Caches the first into lastMode.mmPtr.
function ptrToPat(p) {
  var v = p.toUInt32 ? p.toUInt32() : (parseInt(p.toString(), 16) >>> 0);
  return idPattern(v);
}
function findModeManagerByVtable() {
  var vtG = [ADDR.mmVtable0, ADDR.mmVtable1, ADDR.mmVtable2];
  var vtRt = vtG.map(function (g) { return A(g); });
  var patList = vtRt.map(function (p, i) { return { pat: ptrToPat(p), vt: p, gh: vtG[i] }; });
  var ranges = Process.enumerateRanges({ protection: 'rw-', coalesce: true });
  var scanned = 0, MAXSCAN = 1200 * 1024 * 1024, found = [];
  for (var r = 0; r < ranges.length && scanned < MAXSCAN && found.length < 24; r++) {
    var rng = ranges[r]; scanned += rng.size;
    for (var pi = 0; pi < patList.length && found.length < 24; pi++) {
      var hits = [];
      try { hits = Memory.scanSync(rng.base, rng.size, patList[pi].pat); } catch (e) { continue; }
      for (var h = 0; h < hits.length && found.length < 24; h++) {
        var thisp = hits[h].address; // vptr at object+0
        var id = 0;
        try { id = thisp.add(0x4c).readU32(); } catch (e) { continue; }
        found.push({
          this: thisp.toString(), via: 'vtable',
          inModule: Process.findModuleByAddress(thisp) !== null,
          vtable: thisp.readPointer().toString(),
          vtableGhidra: '0x' + patList[pi].gh.toString(16),
          modeId: '0x' + (id >>> 0).toString(16), modeIdName: nameOf(id)
        });
      }
    }
  }
  var chosen = found.length ? found[0] : null;
  if (chosen) {
    lastMode.mmPtr = ptr(chosen.this);
    lastMode.thisPtr = chosen.this;
    lastMode.id = parseInt(chosen.modeId, 16);
    lastMode.idName = chosen.modeIdName;
    lastMode.at = 'vtable-scan';
  }
  return { scannedBytes: scanned, ranges: ranges.length, count: found.length,
           candidates: found, cachedForSwitch: chosen ? chosen.this : null };
}

// --- Robust vtable discovery (session 8). DumpCallers.java proved FUN_11340560 has NO
// direct callers: it is invoked ONLY as a virtual slot (+0x38) of two vtables in the
// image (0x1200e620, 0x11f910e8). The two static vtables found the exact 4 slots but the
// live object may use a DERIVED vtable we didn't scan for. So instead, scan ALL rw- memory
// for any pointer that equals the dispatch function address -> that IS a vtable slot ->
// vtableBase = slotAddr - 0x38. Enumerate every such live vtable (auto-discovers derived
// classes). Then report how many live objects point at each. Never calls anything.
function findModeVtablesByDispatch() {
  // The vtable stores the function ENTRY address (0x11340560), NOT the mid-function
  // dispatch point (0x113405a0). And vtables live in the IMAGE (r-x/.rdata/.data),
  // not on the rw- heap. So: (1) scan every readable IMAGE range for the entry pointer
  // -> each hit is a vtable slot -> vtableBase = hit - 0x38; (2) for each vtable found
  // in the image, scan the rw- heap for live objects whose vptr == vtableBase.
  var fnAddr = A(ADDR.mmDispatchFn);      // runtime function entry stored in the vtable
  var entryPat = ptrToPat(fnAddr);
  var modRanges = [];
  Process.enumerateRanges({ protection: 'r--', coalesce: false }).concat(
    Process.enumerateRanges({ protection: 'r-x', coalesce: false })).concat(
    Process.enumerateRanges({ protection: 'rw-', coalesce: false })).forEach(function (rng) {
      if (Process.findModuleByAddress(rng.base) !== null) modRanges.push(rng);
    });
  var vtableBases = {};
  for (var r = 0; r < modRanges.length; r++) {
    var hits = [];
    try { hits = Memory.scanSync(modRanges[r].base, modRanges[r].size, entryPat); } catch (e) { continue; }
    for (var h = 0; h < hits.length; h++) {
      var vb = hits[h].address.sub(0x38);
      vtableBases[vb.toString()] = (vtableBases[vb.toString()] || 0) + 1;
    }
  }
  // now scan the rw- heap for live instances of each discovered vtable
  var heapRanges = Process.enumerateRanges({ protection: 'rw-', coalesce: true });
  var bases = Object.keys(vtableBases);
  var vtInfo = [];
  for (var b = 0; b < bases.length; b++) {
    var vb = ptr(bases[b]);
    var objs2 = [];
    for (var r2 = 0; r2 < heapRanges.length; r2++) {
      var hh = [];
      try { hh = Memory.scanSync(heapRanges[r2].base, heapRanges[r2].size, ptrToPat(vb)); } catch (e) { continue; }
      for (var k = 0; k < hh.length && objs2.length < 12; k++) {
        var o = hh[k].address; var id = 0;
        try { id = o.add(0x4c).readU32(); } catch (e) {}
        objs2.push({ this: o.toString(), modeId: '0x' + (id >>> 0).toString(16), modeIdName: nameOf(id) });
      }
      if (objs2.length >= 12) break;
    }
    vtInfo.push({ vtableBase: bases[b], inImage: Process.findModuleByAddress(vb) !== null,
                  slotHits: vtableBases[bases[b]], instances: objs2 });
  }
  // cache the first live instance for switchCoop
  for (var v = 0; v < vtInfo.length; v++) {
    if (vtInfo[v].instances.length) {
      var inst = vtInfo[v].instances[0];
      lastMode.mmPtr = ptr(inst.this);
      lastMode.thisPtr = inst.this;
      lastMode.id = parseInt(inst.modeId, 16);
      lastMode.idName = inst.modeIdName;
      lastMode.at = 'dispatchslot-scan';
      break;
    }
  }
  return { fnEntry: fnAddr.toString(), scannedModRanges: modRanges.length,
           vtableCount: bases.length, vtables: vtInfo,
           cachedForSwitch: lastMode.at === 'dispatchslot-scan' ? lastMode.thisPtr : null };
}

// --- RPC: read the live playlist-service container without calling anything.
rpc.exports = {
  dumpService: function () {
    var out = {};
    // FUN_103d1640 returns &DAT_12863890: the singleton instance is the object AT
    // this address (C++ magic-static guarded by _DAT_1286388c), NOT a pointer stored
    // there. So `this` = the address itself; do NOT readPointer() it. (session 7)
    var svc = A(ADDR.svcSingleton);
    out.service = svc.toString();
    if (!svc.isNull()) {
      try {
        out.c_8c0 = svc.add(0x8c0).readPointer().toString();
        out.c_8c4 = svc.add(0x8c4).readPointer().toString();
      } catch (e) { out.readErr = '' + e; }
    }
    out.idMaskReg = A(ADDR.idMaskReg).readPointer().toString();
    out.centralObj = A(ADDR.centralObj).readPointer().toString();
    out.installG_a = '0x' + A(ADDR.installG_a).readU32().toString(16);
    out.installG_b = '0x' + A(ADDR.installG_b).readU32().toString(16);
    return out;
  },
  lastMode: function () { return lastMode; },
  scanModeManager: function () { return findModeManagerCore(); },
  scanModeManagerByVtable: function () { return findModeManagerByVtable(); },
  scanModeVtables: function () { return findModeVtablesByDispatch(); },
  // Read-only probe of a live mode-manager `this` (from the dispatch hook). Reads the
  // vtable pointer, [this+0x4c] current id, the [this+0x74] gate, and the real targets
  // of vtable slots +0x20/+0x38/+0x5c/+0x60 with a Ghidra-RVA conversion so each can be
  // decompiled offline. Never calls anything. addrStr optional; defaults to lastMode.mmPtr.
  probeMode: function (addrStr) {
    var t = addrStr ? ptr(parseInt(addrStr, 16)) : lastMode.mmPtr;
    if (!t || t.isNull()) return { error: 'no this (pass an address or capture one via the dispatch hook)' };
    function toRva(a) { return '0x' + (a.sub(mod.base).add(0x10000000)).toString(16); }
    var out = { this: t.toString() };
    try { out.curMode = '0x' + (t.add(0x4c).readU32() >>> 0).toString(16); } catch (e) { out.e4c = '' + e; }
    try { out.gate74 = '0x' + (t.add(0x74).readU32() >>> 0).toString(16); } catch (e) {}
    try { out.gate20 = t.add(0x20).readPointer().toString(); } catch (e) {}
    try {
      var vt = t.readPointer();
      out.vtable = vt.toString();
      out.vtableGhidra = toRva(vt);
      out.vtableInImage = Process.findModuleByAddress(vt) !== null;
      var offs = [0x20, 0x38, 0x5c, 0x60];
      out.slots = {};
      for (var i = 0; i < offs.length; i++) {
        var o = offs[i]; var f;
        try { f = vt.add(o).readPointer(); } catch (e) { out.slots['+0x' + o.toString(16)] = 'read-err'; continue; }
        out.slots['+0x' + o.toString(16)] = { addr: f.toString(), ghidra: toRva(f),
          inModule: Process.findModuleByAddress(f) !== null };
      }
    } catch (e) { out.vtableErr = '' + e; }
    return out;
  },
  // Read-only dump of the mode-manager fields the transition path keys on:
  // +0x11 loading-branch flag, +0x19 "transition in progress" gate (must be 0),
  // +0x24 held descriptor, +0x48 PENDING TARGET ID (what FUN_113409d0 actually
  // reads as the destination), +0x4c current id, +0x70 set-to-1 after enqueue.
  mmFields: function (addrStr) {
    var t = addrStr ? ptr(parseInt(addrStr, 16)) : lastMode.mmPtr;
    if (!t || t.isNull()) return { error: 'no this (pass addr or capture via scanModeManagerByVtable)' };
    function b(o) { try { return '0x' + (t.add(o).readU8() >>> 0).toString(16); } catch (e) { return 'err'; } }
    function w(o) { try { return '0x' + (t.add(o).readU32() >>> 0).toString(16); } catch (e) { return 'err'; } }
    return { this: t.toString(), f11_loading: b(0x11), f19_inProgress: b(0x19),
      desc24: w(0x24), pending48: w(0x48), cur4c: w(0x4c), f70: b(0x70), f71: b(0x71) };
  },
  // H4b-v2: set the PENDING TARGET field the loader actually reads (this+0x48) to
  // CO-OP and drive the loader FUN_113409d0(this, &this+0x48, descriptor, 0) which
  // has a CO-OP branch (id 0x43521e6f in its set). dryRun=true only reads+reports.
  loadCoop: function (dryRun, mgrAddrStr, entryAddrStr) {
    var mm = mgrAddrStr ? ptr(parseInt(mgrAddrStr, 16)) : lastMode.mmPtr;
    if (!mm || mm.isNull()) return { error: 'no mode-manager this' };
    var id = MODE.coop;
    var f19 = mm.add(0x19).readU8();
    var info = { modeManager: mm.toString(), before48: '0x' + (mm.add(0x48).readU32() >>> 0).toString(16),
                 cur4c: '0x' + (mm.add(0x4c).readU32() >>> 0).toString(16), inProgress19: f19 };
    // resolve the live CO-OP descriptor (the DAT_128048c0 entry with +0x20==0x43521e6f)
    var entry = entryAddrStr ? ptr(parseInt(entryAddrStr, 16)) : null;
    if (!entry) {
      try {
        var gobj = A(ADDR.idMaskReg).readPointer();
        var data = gobj.add(0x04).readPointer();
        var cnt = gobj.add(0x08).readU32();
        for (var i = 0; i < cnt; i++) {
          var e0 = data.add(i * 4).readPointer();
          if (!e0.isNull() && (e0.add(0x20).readU32() >>> 0) === id) { entry = e0; break; }
        }
      } catch (e) { entry = null; }
    }
    info.descriptor = entry ? entry.toString() : '(null)';
    if (dryRun) { info.dryRun = true; return info; }
    var loader = A(ADDR.loader9d0);   // FUN_113409d0, cdecl (this, &pending, descriptor, p4)
    var p48 = mm.add(0x48);
    mm.add(0x48).writeU32(id >>> 0);  // set the destination the loader reads
    var f = new NativeFunction(loader, 'void', ['pointer', 'pointer', 'pointer', 'pointer']);
    var crashed = false;
    try { f(mm, p48, entry || ptr(0), ptr(0)); } catch (e) { crashed = '' + e; }
    try { info.after48 = '0x' + (mm.add(0x48).readU32() >>> 0).toString(16); } catch (e) {}
    try { info.cur4cAfter = '0x' + (mm.add(0x4c).readU32() >>> 0).toString(16); } catch (e) {}
    try { info.f11After = '0x' + (mm.add(0x11).readU8() >>> 0).toString(16); } catch (e) {}
    info.loaderGhidra = '0x' + loader.sub(mod.base).add(0x10000000).toString(16);
    if (crashed) info.exception = crashed;
    return info;
  },
  // Read-only: the offline co-op gate. FUN_10fa1990 skips the CO-OP branch unless
  // *(DAT_12804acc + 0x6c) != 0 (a co-op/netplay session is available). Read the
  // global both ways (struct-base vs pointer-to-struct) to see which is live.
  netgate: function () {
    var g = A(ADDR.netSess);
    var out = { global: g.toString() };
    try { out.p = g.readPointer().toString(); } catch (e) { out.pErr = '' + e; }
    // interpretation A: DAT_12804acc is the struct base
    try { var _av = '0x' + (g.add(0x6c).readU8() >>> 0).toString(16); out.availBase = _av; } catch (e) {}
    try { out.handleBase = '0x' + (g.add(0x68).readU32() >>> 0).toString(16); } catch (e) {}
    // interpretation B: DAT_12804acc holds a pointer to the struct
    try {
      var sp = g.readPointer();
      if (!sp.isNull()) {
        out.availPtr = '0x' + (sp.add(0x6c).readU8() >>> 0).toString(16);
        out.handlePtr = '0x' + (sp.add(0x68).readU32() >>> 0).toString(16);
        out.availVtable = sp.readPointer().toString();
        out.availVtableGhidra = '0x' + (sp.readPointer().sub(mod.base).add(0x10000000)).toString(16);
      }
    } catch (e) { out.spErr = '' + e; }
    return out;
  },
  // Read-only dump of the NETPLAY SESSION LIST that FUN_103a9ea0 scans. The session-list
  // object is the dword at (DAT_12804acc + 0x68); array = list+0x08, count = list+0x0C;
  // each entry's vtable[+0x04]() returns an info with type at info+0x4 (active: >3) and
  // id at info+0x14. The CO-OP gate also needs entry+0x1c == DAT_1216ca90/DAT_1216ca9c and
  // entry+0x8c / entry+0x90 != -1. Reading the count answers: is there any live session
  // offline (count>0 -> something to reuse; count==0 -> must be fabricated by netplay).
  sessions: function () {
    var g = A(ADDR.netSess);
    var out = {};
    try {
      var list = g.add(0x68).readPointer();  // FUN_103a9ea0 param_1
      out.listObj = list.toString();
      if (!list.isNull()) {
        out.count = list.add(0x0c).readU32();
        out.array = list.add(0x08).readPointer().toString();
        var arr = list.add(0x08).readPointer();
        var cnt = out.count; if (cnt > 32) cnt = 32;
        out.entries = [];
        for (var i = 0; i < cnt; i++) {
          var e = arr.add(i * 4).readPointer();
          var rec = { i: i, e: e.toString() };
          if (!e.isNull()) {
            try { var vt = e.readPointer(); rec.vtable = vt.toString();
              rec.vtableGhidra = '0x' + (vt.sub(mod.base).add(0x10000000)).toString(16); } catch (er) {}
            try { rec.kind1c = '0x' + (e.add(0x1c).readU32() >>> 0).toString(16); } catch (er) {}
            try { rec.f8c = '0x' + (e.add(0x8c).readU32() >>> 0).toString(16); } catch (er) {}
            try { rec.f90 = '0x' + (e.add(0x90).readU32() >>> 0).toString(16); } catch (er) {}
          }
          out.entries.push(rec);
        }
      }
    } catch (e) { out.err = '' + e; }
    return out;
  },
  // Read-only dump of the global mode-list singleton DAT_128048c0 (idMaskReg). The
  // loader (FUN_113409d0) finds a co-op descriptor by scanning this list for the
  // entry whose +0x20 mode id == the target id. Each entry: +0x00 refcount,
  // +0x0C name string (char*), +0x20 mode id. This answers the decisive live question:
  // is a +0x20==0x43521e6f (CO-OP) entry present in the running game offline?
  dumpModes: function (maxEntries) {
    var cap = (maxEntries && maxEntries > 0) ? maxEntries : 64;
    var g = A(ADDR.idMaskReg); // global holding the manager pointer
    var out = { global: g.toString() };
    var obj;
    try { obj = g.readPointer(); } catch (e) { return { error: 'global read fail: ' + e }; }
    out.manager = obj.toString();
    if (obj.isNull()) { out.note = 'singleton null (not constructed yet)'; return out; }
    try { out.vtable = obj.readPointer().toString(); } catch (e) {}
    var data, count;
    try { data = obj.add(0x04).readPointer(); } catch (e) { out.dataErr = '' + e; return out; }
    try { count = obj.add(0x08).readU32(); } catch (e) { out.countErr = '' + e; return out; }
    out.count = count;
    out.entries = [];
    if (data.isNull()) { out.note = 'data ptr null'; return out; }
    var lim = Math.min(count, cap);
    for (var i = 0; i < lim; i++) {
      var ent = { index: i };
      try {
        var e0 = data.add(i * 4).readPointer(); // entry pointer
        ent.entry = e0.toString();
        if (e0.isNull()) { ent.empty = true; out.entries.push(ent); continue; }
        var id = e0.add(0x20).readU32() >>> 0;
        ent.id = '0x' + id.toString(16);
        if (id === MODE.coop) ent.COOP = true;
        var namePtr = e0.add(0x0C).readPointer();
        if (!namePtr.isNull()) {
          try { ent.name = namePtr.readCString(48); } catch (e2) { ent.name = '(unreadable)'; }
        }
      } catch (e) { ent.err = '' + e; }
      out.entries.push(ent);
    }
    return out;
  },
  // H4b - the REAL co-op enter: call modeManager->vtable[+0x0C] (FUN_10fa1990, the
  // mode-change handler) with (&destId, descriptor). NOT vtable+0x5c (the no-op
  // id-setter that switchCoop calls). Needs the live mode-manager `this` (from the
  // dispatch hook OR scanModeManagerByVtable against the primary vtable 0x1200e5f8)
  // and the live CO-OP registry entry (from dumpModes: the entry with +0x20==0x43521e6f).
  // dryRun=true resolves and prints without calling. Calling an engine virtual blind
  // can crash the game: run dryRun first, watch the log AND the game window on go.
  coopEnter: function (dryRun, mgrAddrStr, entryAddrStr) {
    var mm = mgrAddrStr ? ptr(parseInt(mgrAddrStr, 16)) : lastMode.mmPtr;
    if (!mm || mm.isNull()) return { error: 'no mode-manager this (pass addr or capture via scanModeManagerByVtable)' };
    var id = MODE.coop;
    var vt = mm.readPointer();
    var slot = vt.add(0x0c).readPointer();           // *(mgr->vtable + 0x0c) = FUN_10fa1990
    var idBuf = Memory.alloc(4); idBuf.writeU32(id >>> 0);
    var entry = entryAddrStr ? ptr(parseInt(entryAddrStr, 16)) : null;
    // Auto-resolve the live CO-OP registry entry from the DAT_128048c0 singleton when
    // not supplied, so the call uses a same-session address (heap base shifts per run).
    if (!entry) {
      try {
        var gobj = A(ADDR.idMaskReg).readPointer();
        var data = gobj.add(0x04).readPointer();
        var cnt = gobj.add(0x08).readU32();
        for (var i = 0; i < cnt; i++) {
          var e0 = data.add(i * 4).readPointer();
          if (!e0.isNull() && (e0.add(0x20).readU32() >>> 0) === id) { entry = e0; break; }
        }
      } catch (e) { entry = null; }
    }
    var info = { modeManager: mm.toString(), vtable: vt.toString(),
                 vtable0C: slot.toString(),
                 vtable0CGhidra: '0x' + (slot.sub(mod.base).add(0x10000000)).toString(16),
                 curMode: '0x' + (mm.add(0x4c).readU32() >>> 0).toString(16),
                 destId: '0x' + id.toString(16), descriptor: entry ? entry.toString() : '(null)' };
    if (dryRun) { info.dryRun = true; return info; }
    // thiscall: this in ECX, two pointer args (&destId, descriptor) on the stack.
    var f = new NativeFunction(slot, 'int', ['pointer', 'pointer', 'pointer'], 'thiscall');
    var ret = f(mm, idBuf, entry || ptr(0));
    info.ret = ret;
    try { info.modeAfter = '0x' + (mm.add(0x4c).readU32() >>> 0).toString(16); } catch (e) {}
    return info;
  },
  // DANGEROUS, EXPERIMENTAL: write the live mode id [this+0x4c]. Only after the
  // trace confirms `this`; the plan does NOT expect an offline/global poke to
  // switch the mode (H1 demotion), so treat this as a live test, not a fix.
  setModeId: function (thisAddrStr, id) {
    var p = ptr(thisAddrStr).add(0x4c);
    p.writeU32(id >>> 0);
    return { wrote: p.toString(), value: '0x' + (id >>> 0).toString(16),
             nowAt: p.readU32().toString(16) };
  },
  // H3a - switch into co-op. NEEDS the live mode-manager `this` first: enter a
  // menu/lobby once so the dispatch hook caches it (check lastMode() != null),
  // then call switchCoop(false) to write [this+0x4c]=CO-OP and call
  // modeManager->vtable[+0x5c](&id). dryRun=true only shows what it WOULD do.
  // Calling an engine virtual blind can crash the game: run dryRun first.
  switchCoop: function (dryRun) {
    if (!lastMode.mmPtr) return { error: 'no cached mode-manager this; enter a menu so the dispatch hook fires, then check lastMode()' };
    var mm = lastMode.mmPtr;
    var id = MODE.coop;
    var slot = mm.readPointer().add(ADDR.modeSwitchVt).readPointer(); // *(mm->vtable + 0x5c)
    var modeAddr = Memory.alloc(4); modeAddr.writeU32(id >>> 0);
    var cur = mm.add(0x4c).readU32();
    if (dryRun) {
      return { modeManager: mm.toString(), curMode: '0x' + (cur >>> 0).toString(16),
               vtable5c: slot.toString(), argId: '0x' + id.toString(16), dryRun: true };
    }
    mm.add(0x4c).writeU32(id >>> 0);
    // ABI disasm-confirmed (FC3_106, FUN_11340560 @ 0x11340605):
    //   MOV EDX,[EBX] ; MOV EDX,[EDX+0x5c] ; LEA EAX,[&id] ; PUSH EAX ; MOV ECX,EBX ; CALL EDX
    // i.e. thiscall: this in ECX, the single &id argument on the stack. Frida 'thiscall'
    // maps (this, arg) -> (ECX, [esp+4]), matching this exactly.
    var switchFn = new NativeFunction(slot, 'int', ['pointer', 'pointer'], 'thiscall');
    var ret = switchFn(mm, modeAddr); // this=mm (ecx), arg=&id
    return { modeManager: mm.toString(), prevMode: '0x' + (cur >>> 0).toString(16),
             newMode: '0x' + id.toString(16), vtable5c: slot.toString(), ret: ret };
  },
  // H3b - populate the co-op session: call FUN_1127a0f0(service). service `this`
  // is the object AT svcSingleton (0x12863890), not a pointer. dryRun=true only
  // resolves the function address. Same crash caveat as switchCoop.
  populate: function (dryRun) {
    var svc = A(ADDR.svcSingleton);
    var initFn = A(ADDR.svcInit);
    if (dryRun) {
      return { service: svc.toString(), svcInit: initFn.toString(), dryRun: true };
    }
    var f = new NativeFunction(initFn, 'void', ['pointer'], 'thiscall');
    f(svc);
    var c = 'n/a';
    try { c = svc.add(0x8c0).readPointer().toString(); } catch (e) {}
    return { service: svc.toString(), svcInit: initFn.toString(), container8c0: c };
  }
};

console.log('fc3_h3_trace loaded. base=' + base + ' module=' + MODULE +
  ' ; rpc: dumpService(), lastMode(), setModeId(addr,id), switchCoop(dryRun), populate(dryRun)');
