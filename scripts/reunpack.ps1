$ErrorActionPreference = 'Stop'
. E:\FarCryCoop\env.ps1
$bin = 'E:\FarCryCoop\Downloads\gibbed-dunia\src\bin_fc3\Gibbed.FarCry3.Unpack.exe'
$g = 'E:\SteamLibrary\steamapps\common\Far Cry 3\data_win32'
$w = 'E:\FarCryCoop\Work\fc3'
$jobs = @(
    @{ Name = 'common';      Fat = "$g\common.fat" },
    @{ Name = 'multicommon'; Fat = "$g\worlds\multicommon\multicommon.fat" },
    @{ Name = 'fc3_main';    Fat = "$g\worlds\fc3_main\fc3_main.fat" }
)
foreach ($j in $jobs) {
    $new = "$w\$($j.Name).v2"
    if (Test-Path $new) { Remove-Item $new -Recurse -Force }
    & $bin $j.Fat $new | Out-Null
    if ($LASTEXITCODE -ne 0) { throw "unpack failed: $($j.Name) exit $LASTEXITCODE" }
    $empty = (Get-ChildItem "$new\__UNKNOWN\null" -File -ErrorAction SilentlyContinue).Count
    $count = (Get-ChildItem $new -Recurse -File).Count
    "$($j.Name): $count files, null folder: $empty"
    Remove-Item "$w\$($j.Name)" -Recurse -Force
    Rename-Item $new $j.Name
}
Remove-Item "$w\named" -Recurse -Force
python -I "$PSScriptRoot\names.py"
"named empty text files: $((Get-ChildItem "$w\named" -Recurse -File | Where-Object Length -eq 0).Count)"
'DONE'
