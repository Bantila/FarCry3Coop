# Switch a test copy between the vanilla files and our mod files (DLLs + patch archive).
#   switch_variant.ps1 -Game E:\FarCryCoop\Work\game-105 -Variant vanilla|mod
# vanilla: DLLs and patch from the clean source (1.05: Downloads\fc3-1.05, 1.06: the install, read only)
# mod:     DLLs patched by patch_dll.py, patch from Work\mod-build
param([Parameter(Mandatory)][string]$Game, [Parameter(Mandatory)][ValidateSet('vanilla', 'mod')][string]$Variant)
$ErrorActionPreference = 'Stop'
if (Get-Process farcry3, farcry3_d3d11 -ErrorAction SilentlyContinue) { throw "close the game first" }

$src = if ($Game -match '105$') { 'E:\FarCryCoop\Downloads\fc3-1.05' } else { 'E:\SteamLibrary\steamapps\common\Far Cry 3' }
foreach ($dll in 'FC3.dll', 'FC3_d3d11.dll') {
    Remove-Item "$Game\bin\$dll"
    Copy-Item "$src\bin\$dll" "$Game\bin\$dll"
    if ($Variant -eq 'mod') { python -I "$PSScriptRoot\patch_dll.py" "$Game\bin\$dll" }
}
$patchDir = if ($Variant -eq 'mod') { 'E:\FarCryCoop\Work\mod-build' } else { "$src\data_win32" }
foreach ($f in 'patch.fat', 'patch.dat') {
    Remove-Item "$Game\data_win32\$f"          # real copy, not a hard link
    Copy-Item "$patchDir\$f" "$Game\data_win32\$f"
}
"$Game -> $Variant (FC3.dll $((Get-FileHash "$Game\bin\FC3.dll").Hash.Substring(0,12)), patch.fat $((Get-FileHash "$Game\data_win32\patch.fat").Hash.Substring(0,12)))"
