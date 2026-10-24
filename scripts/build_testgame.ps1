# Build a test copy of Far Cry 3 in E:\FarCryCoop\Work\game-<version> without touching the Steam install.
#   bin\         real copy (1.05 from Downloads\fc3-1.05, 1.06 from the install)
#   data_win32\  hard links to the install's archives, except patch* / igepatch* (real copies of the
#                wanted version; our mod later replaces patch.dat/fat with new files)
# Hard links share data with the install: never edit a linked file in place; replace it with a new file.
param([Parameter(Mandatory)][ValidateSet('1.05', '1.06')][string]$Version)
$ErrorActionPreference = 'Stop'

$install = 'E:\SteamLibrary\steamapps\common\Far Cry 3'
$v105 = 'E:\FarCryCoop\Downloads\fc3-1.05'
$dst = "E:\FarCryCoop\Work\game-$($Version.Replace('.', ''))"
$binSrc = if ($Version -eq '1.05') { "$v105\bin" } else { "$install\bin" }
$patchSrc = if ($Version -eq '1.05') { "$v105\data_win32" } else { "$install\data_win32" }

if (Test-Path $dst) { throw "$dst exists; remove it first" }
New-Item -ItemType Directory "$dst\data_win32" | Out-Null
Copy-Item $binSrc "$dst\bin" -Recurse

$linked = 0; $copied = 0
Get-ChildItem "$install\data_win32" -Recurse -File | ForEach-Object {
    $rel = $_.FullName.Substring("$install\data_win32\".Length)
    $target = Join-Path "$dst\data_win32" $rel
    New-Item -ItemType Directory -Force (Split-Path $target) | Out-Null
    if ($rel -match '^(ige)?patch[^\\]*$') {
        $src = Join-Path $patchSrc $rel
        if (-not (Test-Path $src)) { $src = $_.FullName }   # e.g. patch_german only in one version
        Copy-Item $src $target; $copied++
    } else {
        New-Item -ItemType HardLink -Path $target -Target $_.FullName | Out-Null; $linked++
    }
}
# 1.05 ships multicommon_japanese.*, which 1.06 dropped (manifest_diff.py)
if ($Version -eq '1.05') {
    foreach ($f in 'multicommon_japanese.dat', 'multicommon_japanese.fat') {
        $src = "$v105\data_win32\worlds\multicommon\$f"
        if (Test-Path $src) { Copy-Item $src "$dst\data_win32\worlds\multicommon\$f"; $copied++ }
        else { Write-Warning "$src missing: download it with fc3-105-japanese-filelist.txt" }
    }
}
"$dst : bin copied from $binSrc; data_win32: $linked hard links, $copied real copies (patch from $patchSrc)"
