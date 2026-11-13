// fc3_coop_trace.js - Frida: trace Far Cry 3 co-op service connection (direction B recon).
// Attach to farcry3_d3d11.exe (launched via Ubisoft Connect), then navigate main menu -> co-op.
// Core = winsock hooks (module-independent): reveal the co-op service host:port + connect/DNS failures.
// Best-effort = FC3.dll gate offsets (may not resolve if the running build differs).
'use strict';
// Use send() (guaranteed delivered to the python host via on_message 'send'); console.log is not captured there.
var log = function(){ var a=Array.prototype.slice.call(arguments).join(' '); try { send(a); } catch(e) { console.log(a); } };

// hex of first n bytes at p (guarded).
function hex(p, n){ try { var b=p.readByteArray(n); if(!b) return ''; var u=new Uint8Array(b), s=''; for(var i=0;i<u.length;i++){ s+=(u[i]<16?'0':'')+u[i].toString(16); } return s; } catch(e){ return '<bad>'; } }

// ---------- game-module attribution + call-stack backtrace (direction B: name the RV callers) ----------
var MODS = Process.enumerateModules().map(function(m){ return { base:m.base, end:m.base.add(m.size), name:m.name }; });
function findMod(a){ for (var i=0;i<MODS.length;i++){ if (a.compare(MODS[i].base)>=0 && a.compare(MODS[i].end)<0) return MODS[i]; } return null; }
function isGame(s){ return /farcry3|^FC3/i.test(s); }
function fmtAddr(a){ var m=findMod(a); if(!m) return null; return m.name+'+0x'+a.sub(m.base).toString(16); }
function gameFrames(ctx, mode){
  var fr=[]; try { fr = Thread.backtrace(ctx, mode); } catch(e){ return []; }
  var out=[]; for (var i=0;i<fr.length;i++){ var f=fmtAddr(fr[i]); if(f && isGame(f)) out.push(f); }
  return out;
}
function bt(ctx){
  var g = gameFrames(ctx, Backtracer.ACCURATE);
  if (g.length < 2){ var fz = gameFrames(ctx, Backtracer.FUZZY); if (fz.length > g.length) g = fz; }
  return g.slice(0,12).join(' <- ');
}
function isRv(s){ return s && (s.indexOf(':1100')>=0 || s.indexOf('203.132.26')>=0 || s.indexOf(':3074')>=0); }

// ---------- winsock ----------
function sockaddrInfo(p){
  try {
    var fam = p.readU16();
    if (fam !== 2 /*AF_INET*/) return {fam: fam, s: 'fam='+fam};
    var port = (p.add(2).readU8()<<8) | p.add(3).readU8();   // network order -> host
    var ipBytes = p.add(4).readByteArray(4);
    var b = new Uint8Array(ipBytes);
    return {fam: fam, s: b[0]+'.'+b[1]+'.'+b[2]+'.'+b[3]+':'+port};
  } catch(e){ return {s:'<bad sockaddr>'}; }
}
['ws2_32.dll','ws2_32'].forEach(function(mod){
  var m = Process.findModuleByName(mod); if(!m) return;
  var ghn = m.findExportByName('gethostbyname');
  if (ghn) Interceptor.attach(ghn, { onEnter:function(args){ this.n = args[0].readCString(); this.ctx=this.context; },
    onLeave:function(r){ if(!this.n || this.n.indexOf('.')<0) return; var hosts=''; if(!r.isNull()){ try{ hosts=r.readPointer().readCString(); }catch(e){} }
      log('[DNS] gethostbyname("' + this.n + '") -> ' + (r.isNull()?'NULL(fail)':('hostent name='+hosts)));
      if (/ubisoft|rdv/i.test(this.n)) log('[RV-BT] gethostbyname("'+this.n+'") callers: '+bt(this.ctx)); } });
  var gai = m.findExportByName('getaddrinfo');
  if (gai) Interceptor.attach(gai, { onEnter:function(args){ this.node = args[0].isNull()?'null':args[0].readCString(); this.svc = args[1].isNull()?'null':args[1].readCString(); },
    onLeave:function(r){ log('[DNS] getaddrinfo(node="'+this.node+'", svc="'+this.svc+'") -> ret='+r); } });
  var con = m.findExportByName('connect');
  if (con) Interceptor.attach(con, { onEnter:function(args){ var si = sockaddrInfo(args[1]); this.si=si.s; this.ctx=this.context; },
    onLeave:function(r){ log('[NET] connect(fd, '+this.si+') -> '+r.toInt32()+(r.toInt32()===0?' OK':' (WSAErro r '+(r.toInt32()<0?(-r.toInt32()):r.toInt32())+')')); if(isRv(this.si)) log('[RV-BT] connect('+this.si+') callers: '+bt(this.ctx)); } });
  var sto = m.findExportByName('sendto');
  if (sto) Interceptor.attach(sto, { onEnter:function(args){ this.dst = args[4].isNull()?'<none/connected>':sockaddrInfo(args[4]).s; this.len=args[2].toInt32(); this.buf=args[1]; this.ctx=this.context; },
    onLeave:function(r){ if(this.len>0) log('[NET] sendto(fd, len='+this.len+', dst='+this.dst+') -> '+r.toInt32()+' data='+hex(this.buf, Math.min(this.len,64)));
      if(isRv(this.dst)) log('[RV-BT] sendto->'+this.dst+' callers: '+bt(this.ctx)); } });
  var rfo = m.findExportByName('recvfrom');
  if (rfo) Interceptor.attach(rfo, { onEnter:function(args){ this.src = args[4].isNull()?'<none>':sockaddrInfo(args[4]).s; this.buf=args[1]; },
    onLeave:function(r){ var n=r.toInt32(); if(n>0) log('[NET] recvfrom(fd, n='+n+', src='+this.src+') data='+hex(this.buf, Math.min(n,64))); } });
  var bnd = m.findExportByName('bind');
  if (bnd) Interceptor.attach(bnd, { onEnter:function(args){ this.sa=sockaddrInfo(args[1]).s; this.ctx=this.context; log('[NET] bind(fd, '+this.sa+')'); },
    onLeave:function(r){ if(/:3074|:9000/.test(this.sa)) log('[RV-BT] bind('+this.sa+') callers: '+bt(this.ctx)); } });
  var snd = m.findExportByName('send');
  if (snd) Interceptor.attach(snd, { onEnter:function(a){ this.fd=a[0]; this.buf=a[1]; this.len=a[2].toInt32(); },
    onLeave:function(r){ if(this.len>0 && r.toInt32()>0) log('[NET] send(fd='+this.fd+', n='+r.toInt32()+') data='+hex(this.buf, Math.min(this.len,64))); } });
  var rcv = m.findExportByName('recv');
  if (rcv) Interceptor.attach(rcv, { onEnter:function(a){ this.buf=a[1]; },
    onLeave:function(r){ if(r.toInt32()>0) log('[NET] recv(n='+r.toInt32()+') data='+hex(this.buf, Math.min(r.toInt32(),64))); } });
  log('winsock hooks installed on '+mod);
});

// ---------- running-module RV/echo chains (direction B), FC3_d3d11.dll copy md5 46bcc097 ----------
function tryGate(){
  var names = ['FC3_d3d11.dll','FC3.dll'];
  for (var i=0;i<names.length;i++){
    var m = Process.findModuleByName(names[i]); if(!m) continue;
    var base = m.base;
    // RVA = addr - 0x10000000 (module base); chains named by live backtraces (Session 28q)
    var offs = { 'rv_resolver_0x122f759':0x122f759, 'rv_0x122f96f':0x122f96f, 'rv_0x123311e':0x123311e,
                 'rv_0x1279bc5':0x1279bc5, 'rv_0x127a320':0x127a320, 'rv_0x127a3d2':0x127a3d2,
                 'echo_bind_0xe5be2c':0xe5be2c, 'echo_0x41a795':0x41a795, 'echo_pump_0x550d96':0x550d96 };
    Object.keys(offs).forEach(function(k){
      try { Interceptor.attach(base.add(offs[k]), { onEnter:function(args){ log('[RV] hit '+k+' (a0='+args[0]+')'); } }); }
      catch(e){ log('[RV] hook '+k+' failed: '+e.message); }
    });
    log('module RV/echo hooks attempted on '+names[i]+' base='+base);
  }
}
setTimeout(tryGate, 1500);
log('fc3_coop_trace loaded. Navigate to co-op in-game now.');
