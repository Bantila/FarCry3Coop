@echo off
rem build.bat - generated: 32-bit uplay_r1_loader proxy via MSVC
rem NOTE: target is x86 (/MACHINE:X86, /DWIN32); use the 32-bit toolchain (vcvars32), not vcvars64.
call "C:\Program Files\Microsoft Visual Studio\18\Community\VC\Auxiliary\Build\vcvars32.bat" >nul
if not exist obj mkdir obj
cl /nologo /W3 /O2 /MT /LD /DWIN32 /Fo"obj\\" uplay_proxy.cpp /Fe"uplay_r1_loader.dll" /link /DEF:uplay_proxy.def /MACHINE:X86
echo BUILD_DONE %errorlevel%
