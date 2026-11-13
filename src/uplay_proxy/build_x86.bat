@echo off
rem NOTE: target is x86 (/MACHINE:X86, /DWIN32); use the 32-bit toolchain (vcvars32). vcvars64 -arch= does not set up env in VS18.
call "C:\Program Files\Microsoft Visual Studio\18\Community\VC\Auxiliary\Build\vcvars32.bat" >vc.log 2>&1
where cl >nul 2>&1 || (echo NO_CL & exit /b 1)
if not exist obj mkdir obj
cl /nologo /W3 /O1 /MT /LD /DWIN32 /Fo"obj\\" uplay_proxy.cpp /Fe"uplay_r1_loader.dll" /link /DEF:uplay_proxy.def /MACHINE:X86 >build.log 2>&1
echo BUILD_DONE %errorlevel%
