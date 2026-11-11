@echo off
setlocal
REM Run DumpCallers.java against the already-analyzed FC3_106 project (no re-analysis).
REM Output (CALL/DATA xrefs to FUN_11340560) lands in %LOG%.
set "GHIDRA_HOME=C:\tools\ghidra_12.1.4_PUBLIC"
set "JAVA_HOME=C:\tools\jdk-21.0.13+9"
set "WORK=H:\FarCryCoop\scratch\ghidra"
set "PROJ=%WORK%\proj"
set "TMP=%WORK%\tmp"
set "TEMP=%WORK%\tmp"
set "JAVA_TOOL_OPTIONS=-Xmx8g -Djava.io.tmpdir=%WORK%\tmp"
if exist "%PROJ%\FC3_106.lock" del "%PROJ%\FC3_106.lock"
if exist "%PROJ%\FC3_106.lock~" del "%PROJ%\FC3_106.lock~"
set "DONE=%WORK%\CALLERS_DONE.txt"
set "LOG=%WORK%\callers.log"
if exist "%DONE%" del "%DONE%"
echo started %DATE% %TIME% > "%WORK%\CALLERS_STARTED.txt"
call "%GHIDRA_HOME%\support\analyzeHeadless.bat" "%PROJ%" FC3_106 -process "FC3.dll" -noanalysis -scriptPath "%WORK%\scripts" -postScript DumpCallers.java > "%LOG%" 2>&1
echo exit=%ERRORLEVEL% finished %DATE% %TIME% > "%DONE%"
endlocal
