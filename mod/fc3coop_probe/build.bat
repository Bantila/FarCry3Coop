@echo off
REM build.bat -- compile the FC3 co-op H1 probe into a 32-bit dinput8.dll proxy.
REM
REM Uses the MSVC x86 toolchain (vcvars32.bat) with the static CRT (/MT) so the DLL
REM has no VC redist dependency. Exports come from dinput8.def (6 names, ordinals 1..6).
REM Output: build\dinput8.dll  (intermediates stay in build\; nothing is copied anywhere)

setlocal

set "SRC_DIR=%~dp0"
set "OUT_DIR=%SRC_DIR%build"
set "VCVARS=C:\Program Files\Microsoft Visual Studio\18\Community\VC\Auxiliary\Build\vcvars32.bat"

if not exist "%VCVARS%" (
    echo [build] ERROR: vcvars32.bat not found at "%VCVARS%"
    exit /b 2
)

if not exist "%OUT_DIR%" mkdir "%OUT_DIR%"

echo [build] initializing MSVC x86 environment...
call "%VCVARS%"
if errorlevel 1 (
    echo [build] ERROR: vcvars32.bat failed
    exit /b 3
)

echo [build] resolving compiler tools:
where cl
where link

REM Build inside build\ so every intermediate (.obj/.exp/.lib) lands there too.
REM The repo path contains a space, so relative names are used instead of quoted /Fo.
pushd "%OUT_DIR%"
echo [build] compiling fc3coop_probe.c ...
REM NOTE: the .def is handed to the linker via /DEF, NOT as a cl input file: with /TC
REM cl would compile dinput8.def as C source and fail with syntax errors.
REM /IGNORE:4104 silences "export of DllCanUnloadNow should be PRIVATE": we DO want the
REM Dll* names exported, because the real dinput8.dll exports them by name and ordinal.
cl /nologo /LD /O2 /MT /W3 /EHsc /TC ..\fc3coop_probe.c /Fe:dinput8.dll /link /NOLOGO /DEF:..\dinput8.def /IGNORE:4104 /MACHINE:X86 /OPT:REF /OPT:ICF kernel32.lib user32.lib
set "RC=%ERRORLEVEL%"
popd

if not "%RC%"=="0" (
    echo [build] FAILED: cl exited with %RC%
    exit /b %RC%
)

if not exist "%OUT_DIR%\dinput8.dll" (
    echo [build] FAILED: %OUT_DIR%\dinput8.dll was not produced
    exit /b 4
)

echo [build] OK: %OUT_DIR%\dinput8.dll
dir "%OUT_DIR%\dinput8.dll"
exit /b 0
