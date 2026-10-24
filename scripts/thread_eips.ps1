# Sample the instruction pointer (EIP) of the busiest threads of a 32-bit game process, to see where it hangs.
# Usage: thread_eips.ps1 -ProcessId <pid> [-Top 6] [-Samples 5]
# Each thread is suspended for a moment (Wow64GetThreadContext), so the game keeps running.
param([Parameter(Mandatory)][int]$ProcessId, [int]$Top = 6, [int]$Samples = 5)
Add-Type @'
using System; using System.Runtime.InteropServices;
public static class Th {
  [DllImport("kernel32.dll")] public static extern IntPtr OpenThread(int access, bool inherit, int id);
  [DllImport("kernel32.dll")] public static extern int SuspendThread(IntPtr h);
  [DllImport("kernel32.dll")] public static extern int ResumeThread(IntPtr h);
  [DllImport("kernel32.dll")] public static extern bool CloseHandle(IntPtr h);
  [DllImport("kernel32.dll")] public static extern bool Wow64GetThreadContext(IntPtr h, byte[] ctx);
  // WOW64_CONTEXT is 716 bytes; ContextFlags at 0, Eip at 0xB8, Esp at 0xC4
  public static uint[] EipEsp(int tid) {
    IntPtr h = OpenThread(0x0002 | 0x0008 | 0x0040, false, tid);  // SUSPEND_RESUME | GET_CONTEXT | QUERY_INFORMATION
    if (h == IntPtr.Zero) return null;
    try {
      byte[] c = new byte[716];
      BitConverter.GetBytes(0x00010001).CopyTo(c, 0);  // WOW64_CONTEXT_CONTROL
      if (SuspendThread(h) < 0) return null;
      bool ok = Wow64GetThreadContext(h, c);
      ResumeThread(h);
      return ok ? new uint[] { BitConverter.ToUInt32(c, 0xB8), BitConverter.ToUInt32(c, 0xC4) } : null;
    } finally { CloseHandle(h); }
  }
  [DllImport("kernel32.dll")] public static extern IntPtr OpenProcess(int access, bool inherit, int id);
  [DllImport("kernel32.dll")] public static extern bool ReadProcessMemory(IntPtr p, IntPtr a, byte[] b, int n, out IntPtr read);
  public static uint[] Stack(int pid, uint esp, int words) {
    IntPtr p = OpenProcess(0x0010, false, pid);  // VM_READ
    byte[] b = new byte[words * 4]; IntPtr r;
    ReadProcessMemory(p, new IntPtr(esp), b, b.Length, out r);
    CloseHandle(p);
    var w = new uint[r.ToInt32() / 4];
    for (int i = 0; i < w.Length; i++) w[i] = BitConverter.ToUInt32(b, i * 4);
    return w;
  }
  [DllImport("psapi.dll")] public static extern bool EnumProcessModulesEx(IntPtr p, IntPtr[] mods, int cb, out int needed, int filter);
  [DllImport("psapi.dll", CharSet = CharSet.Unicode)] public static extern int GetModuleBaseNameW(IntPtr p, IntPtr m, System.Text.StringBuilder s, int n);
  [StructLayout(LayoutKind.Sequential)] public struct MI { public IntPtr Base; public int Size; public IntPtr Entry; }
  [DllImport("psapi.dll")] public static extern bool GetModuleInformation(IntPtr p, IntPtr m, out MI mi, int cb);
  // Process.Modules from a 64-bit host lists only the 64-bit modules of a WOW64 process; ask for the 32-bit ones
  public static string[] Modules32(int pid) {
    IntPtr p = OpenProcess(0x0410, false, pid);  // QUERY_INFORMATION | VM_READ
    IntPtr[] m = new IntPtr[1024]; int need;
    EnumProcessModulesEx(p, m, m.Length * IntPtr.Size, out need, 1);  // LIST_MODULES_32BIT
    var res = new System.Collections.Generic.List<string>();
    for (int i = 0; i < need / IntPtr.Size; i++) {
      var sb = new System.Text.StringBuilder(260); MI mi;
      GetModuleBaseNameW(p, m[i], sb, 260);
      GetModuleInformation(p, m[i], out mi, Marshal.SizeOf(typeof(MI)));
      res.Add(sb + "|" + mi.Base.ToInt64() + "|" + mi.Size);
    }
    CloseHandle(p);
    return res.ToArray();
  }
}
'@
$p = Get-Process -Id $ProcessId
$mods = [Th]::Modules32($ProcessId) | ForEach-Object { $n, $b, $s = $_ -split '\|'; [pscustomobject]@{ Name = $n; Base = [int64]$b; End = [int64]$b + [int64]$s } }
function Where-Eip([int64]$eip) {
    $m = $mods | Where-Object { $eip -ge $_.Base -and $eip -lt $_.End } | Select-Object -First 1
    if ($m) { '{0}+0x{1:x}' -f $m.Name, ($eip - $m.Base) } else { '0x{0:x8}' -f $eip }
}
$t0 = @{}; $p.Threads | ForEach-Object { $t0[$_.Id] = $_.TotalProcessorTime.TotalMilliseconds }
Start-Sleep -Seconds 2
$p.Refresh()
$hot = $p.Threads | ForEach-Object { [pscustomobject]@{ Id = $_.Id; Ms = [int]($_.TotalProcessorTime.TotalMilliseconds - $t0[$_.Id]) } } |
    Sort-Object Ms -Descending | Select-Object -First $Top
foreach ($t in $hot) {
    $where = 1..$Samples | ForEach-Object { $r = [Th]::EipEsp($t.Id); if ($r) { Where-Eip $r[0] }; Start-Sleep -Milliseconds 150 }
    "tid {0,6}  cpu {1,5} ms/2s  {2}" -f $t.Id, $t.Ms, (($where | Group-Object | Sort-Object Count -Descending | ForEach-Object { "$($_.Name) x$($_.Count)" }) -join ', ')
    if ($t -eq $hot[0]) {
        # Raw stack scan of the busiest thread: values that point into FC3*.dll are likely return addresses.
        $r = [Th]::EipEsp($t.Id)
        $fc3 = $mods | Where-Object Name -like 'FC3*'
        $ret = [Th]::Stack($ProcessId, $r[1], 4096) | Where-Object { $v = [int64]$_; $fc3 | Where-Object { $v -ge $_.Base -and $v -lt $_.End } }
        "  FC3 addresses on its stack (top first, preferred base 0x10000000):"
        foreach ($v in ($ret | Select-Object -First 25)) {
            $m = $fc3 | Where-Object { [int64]$v -ge $_.Base -and [int64]$v -lt $_.End } | Select-Object -First 1
            "    {0} 0x{1:x8}" -f $m.Name, ([int64]$v - $m.Base + 0x10000000)
        }
    }
}
