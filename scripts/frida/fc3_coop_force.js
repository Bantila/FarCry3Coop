// fc3_coop_force.js - in-memory direction-B go/no-go probe (NO disk writes). FC3_d3d11.dll copy md5 46bcc097.
// Observes the net mode + online-coop entry, and forces the RendezVous online gate to "succeed" to see where it dead-ends.
'use strict';
var log = function(){ var a=Array.prototype.slice.call(arguments).join(' '); try { send(a); } catch(e) { console.log(a); } };
var FORCE = true;   // when true, force the RV gate to return success; set false for pure observation
var FORCE_LAN_MODE = false; // when true, force net-engine mode field to 0 (LAN) at init

function rvOf(m, rva){ return m.base.add(rva); }
function findGame(){ return Process.findModuleByName('FC3_d3d11.dll'); }

function forceRet(addr, val, name){
  try {
    Interceptor.attach(addr, { onEnter: function(){ this.hit=true; },
      onLeave: function(r){ if(FORCE){ this.returnValue = ptr(val); } log('[FORCE] '+name+' -> '+(FORCE?val:('orig '+r))); } });
    log('[ok] hooked '+name+' @ '+addr);
  } catch(e){ log('[fail] hook '+name+' @ '+addr+': '+e.message); }
}
function logRet(addr, name){
  try { Interceptor.attach(addr, { onLeave: function(r){ log('[obs] '+name+' -> '+r); } }); log('[ok] obs '+name); }
  catch(e){ log('[fail] obs '+name+': '+e.message); }
}

function go(){
  var m = findGame(); if(!m){ log('FC3_d3d11.dll not found'); return; }
  log('FC3_d3d11.dll base='+m.base+'  (FORCE='+FORCE+', FORCE_LAN_MODE='+FORCE_LAN_MODE+')');

  // net-engine init: log the connection mode (param_1[0xe]: 0=LAN,1=Online,2=Offline)
  try { Interceptor.attach(rvOf(m,0x92d256), { onEnter: function(a){
    var mm = -1; try { mm = a[0].add(0x38).readU8(); } catch(e){}
    if (FORCE_LAN_MODE){ try { a[0].add(0x38).writeU8(0); } catch(e){} }
    log('[obs] net-init mode field = '+mm+' ('+(mm===0?'LAN':mm===1?'Online':mm===2?'Offline':'?')+')');
  }}); log('[ok] obs net-init mode'); } catch(e){ log('[fail] net-init: '+e.message); }

  // game entry into the online-coop RV flow
  try { Interceptor.attach(rvOf(m,0x44123b), { onEnter: function(){ log('[obs] game entered online-coop RV flow (FUN_1044123b)'); } }); log('[ok] obs RV entry'); } catch(e){ log('[fail] RV entry: '+e.message); }

  if (FORCE) {
    forceRet(rvOf(m,0x1245090), 1, 'FUN_11245090(online-flag)'); // return DAT_11f07e48 -> force 1
    forceRet(rvOf(m,0x12492a0), 1, 'FUN_112492a0(rv-netop)');
    forceRet(rvOf(m,0x1279ba0), 1, 'FUN_11279ba0(rv-gate)');
    logRet(rvOf(m,0x127a1d0), 'FUN_1127a1d0(post-RV->UbiAuth)'); // if this hits, we passed the gate
  } else {
    logRet(rvOf(m,0x12492a0), 'FUN_112492a0');
    logRet(rvOf(m,0x1279ba0), 'FUN_11279ba0(gate)');
  }
  log('fc3_coop_force loaded. Navigate co-op -> connect, and watch [obs]/[FORCE]/[NET] lines.');
}

// keep the winsock + RV backtrace hooks from the tracer for network visibility
function installNet(){
  ['ws2_32.dll'].forEach(function(mod){
    var m=Process.findModuleByName(mod); if(!m) return;
    var ghn=m.findExportByName('gethostbyname');
    if(ghn) Interceptor.attach(ghn,{onEnter:function(a){this.n=a[0].readCString();},onLeave:function(r){ if(this.n&&this.n.indexOf('.')>=0) log('[DNS] '+this.n+' -> '+(r.isNull()?'FAIL':'ok')); }});
    var sto=m.findExportByName('sendto');
    if(sto) Interceptor.attach(sto,{onEnter:function(a){ this.dst=a[4].isNull()?'<conn>':'<to>'; this.buf=a[1]; this.len=a[2].toInt32(); },
      onLeave:function(r){ if(this.len>0&&this.len<80) log('[NET] sendto len='+this.len+' -> '+r.toInt32()); }});
    var c=m.findExportByName('connect');
    if(c) Interceptor.attach(c,{onEnter:function(a){ try{var p=(a[1].add(2).readU8()<<8)|a[1].add(3).readU8(); var b=new Uint8Array(a[1].add(4).readByteArray(4)); this.s=b[0]+'.'+b[1]+'.'+b[2]+'.'+b[3]+':'+p;}catch(e){this.s='?';} },
      onLeave:function(r){ log('[NET] connect '+this.s+' -> '+r.toInt32()); }});
  });
}

setTimeout(function(){ installNet(); go(); }, 1200);
