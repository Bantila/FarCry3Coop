# Start the 1.05 test copy with the developers' quick-launch switches (FUN_10652061 in FC3.dll 1.05):
#   host:   -host <map> -login <name> -coop        (no -online -> session type 3, local, no Ubisoft services)
#   client: -client -login <name> -ip <address> -coop
# Windowed DX11 (farcry3_d3d11.exe, -Dx9 for farcry3.exe), placed side by side so two instances fit on one screen.
param(
    [Parameter(Mandatory)][ValidateSet('host', 'client')][string]$Role,
    [string]$Map = 'coop_vidar',          # coop_vidar, coop_skadi, coop_freyja, coop_huginn, coop_sleipnir, coop_fenrir
    [string]$Ip = '127.0.0.1',
    [int]$Width = 1280,
    [int]$Height = 720,
    [switch]$Dx9                          # farcry3.exe; its windowed picture freezes in a co-op session
)
$exe = if ($Dx9) { 'E:\FarCryCoop\Work\game-105\bin\farcry3.exe' } else { 'E:\FarCryCoop\Work\game-105\bin\farcry3_d3d11.exe' }
if ($Role -eq 'host') {
    $gameArgs = "-host $Map -login Host -coop -xpos 0 -ypos 0 -xres $Width -yres $Height"
} else {
    $gameArgs = "-client -login Guest -ip $Ip -coop -xpos $Width -ypos 0 -xres $Width -yres $Height"
}
"starting: $exe $gameArgs"
Start-Process -FilePath $exe -ArgumentList $gameArgs -WorkingDirectory (Split-Path $exe)
