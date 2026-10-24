# Build patch.dat/fat for the test copies: vanilla patch content + our files, packed with Gibbed.FarCry3.Pack.
# The vanilla patch archive is the same in 1.05 and 1.06 (patch.fat SHA-256 39DC4178...).
$ErrorActionPreference = 'Stop'
. E:\FarCryCoop\env.ps1

$pack = 'E:\FarCryCoop\Downloads\gibbed-dunia\src\bin_fc3\Gibbed.FarCry3.Pack.exe'
$unpack = 'E:\FarCryCoop\Downloads\gibbed-dunia\src\bin_fc3\Gibbed.FarCry3.Unpack.exe'
$build = 'E:\FarCryCoop\Work\mod-build'
$tree = "$build\patch"

if (Test-Path $tree) { Remove-Item $tree -Recurse -Force }
Copy-Item 'E:\FarCryCoop\Work\fc3\patch' $tree -Recurse                      # vanilla, __UNKNOWN\<type>\<hash>.<ext>

# our files under their real names (the packer hashes the path)
New-Item -ItemType Directory -Force "$tree\generated", "$tree\ui\multiplayer\menu" | Out-Null
Copy-Item "$build\nomad\nomadobjecttemplates_new.fcb" "$tree\generated\nomadobjecttemplates.fcb"   # Local Coop: 1 player, 10 s countdown
# TEST ONLY, third-party file from Nexus mod 262 (not ours, never ship it): multiplayer main menu
Copy-Item 'E:\FarCryCoop\Work\fc3-105\mod262-patch\__UNKNOWN\ui\E88B7431DC8E7DBF.feu' "$tree\ui\multiplayer\menu\multimain.feu"

& $pack "$build\patch.fat" $tree | Out-Null
if ($LASTEXITCODE -ne 0) { throw "pack failed" }

# check: unpack again, expect vanilla + 2 files
$check = "$build\check"
if (Test-Path $check) { Remove-Item $check -Recurse -Force }
& $unpack "$build\patch.fat" $check | Out-Null
$n = (Get-ChildItem $check -Recurse -File).Count
$ours = Get-ChildItem $check -Recurse -File | Where-Object { $_.Name -match '^(9B788D77FCFA35BB|E88B7431DC8E7DBF)' }
"patch.fat: $n files; ours present: $($ours.Name -join ', ')"
if ($n -ne 429 -or $ours.Count -ne 2) { throw "unexpected archive content" }

foreach ($g in 'E:\FarCryCoop\Work\game-105', 'E:\FarCryCoop\Work\game-106') {
    foreach ($f in 'patch.fat', 'patch.dat') {
        $t = "$g\data_win32\$f"
        Remove-Item $t   # real copy (not a hard link), safe to replace
        Copy-Item "$build\$f" $t
    }
    "$g : patch replaced"
}
