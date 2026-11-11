@echo off
setlocal
rem fc3_h3_run.bat - one-command launcher for the H3 live test.
rem Attaches Frida to the running FC3 game (farcry3.exe / farcry3_d3d11.exe),
rem loads fc3_h3_trace.js, and mirrors the whole session to H:\FarCryCoop\scratch\h3_live.log
rem (any previous log is backed up first). Run the game OFFLINE to the main menu first.
rem Pass a pid to skip auto-detect:   fc3_h3_run.bat --pid 1234
chcp 65001 >nul
set PYTHONUTF8=1
cd /d "%~dp0"
python "%~dp0fc3_h3_run.py" %*
echo.
echo (log written to H:\FarCryCoop\scratch\h3_live.log)
endlocal
