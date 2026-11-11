@echo off
setlocal
REM Run DecompileH3.java against the already-analyzed FC3_106 project (no re-analysis).
set "GHIDRA_HOME=C:\tools\ghidra_12.1.4_PUBLIC"
set "JAVA_HOME=C:\tools\jdk-21.0.13+9"
set "WORK=H:\FarCryCoop\scratch\ghidra"
set "PROJ=%WORK%\proj"
set "TMP=%WORK%\tmp"
set "TEMP=%WORK%\tmp"
set "JAVA_TOOL_OPTIONS=-Xmx8g -Djava.io.tmpdir=%WORK%\tmp"
if exist "%PROJ%\FC3_106.lock" del "%PROJ%\FC3_106.lock"
if exist "%PROJ%\FC3_106.lock~" del "%PROJ%\FC3_106.lock~"
set "DONE=%WORK%\DECOMP_DONE.txt"
set "LOG=%WORK%\decomp.log"
if exist "%DONE%" del "%DONE%"
echo started %DATE% %TIME% > "%WORK%\DECOMP_STARTED.txt"
call "%GHIDRA_HOME%\support\analyzeHeadless.bat" "%PROJ%" FC3_106 -process "FC3.dll" -noanalysis -scriptPath "%WORK%\scripts" -postScript DecompileH3.java > "%LOG%" 2>&1
echo exit=%ERRORLEVEL% finished %DATE% %TIME% > "%DONE%"
endlocal
