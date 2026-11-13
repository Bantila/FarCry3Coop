// orbit_shim.cpp - pass-through logging shim for Far Cry 3 (32-bit) orbit-API traffic.
// Deployed as bin\d3d9.dll (proxy for the real system d3d9.dll).
//
// Design (see PLAN "orbit-API responder", step 1 of 2 - observation only):
//  * IAT hook: every loaded module's import of kernel32!GetProcAddress /
//    GetProcAddressForANSIString is redirected to our hook (IAT writes only -
//    no inline kernel patches, no loader-lock games).
//  * When any module requests "OrbitApi_InterfaceRequest", we log the requesting
//    module!RVA (friendly tags for known netplay RVAs), resolve the REAL export
//    from uplay_r14.dll / uplay_r2.dll (scanning all modules if needed), remember
//    it, and hand the caller our logging wrapper instead.
//  * The wrapper logs every orbit call: interfaceId, first 12 DWORD args, the
//    caller's return address, plausible code addresses found on the stack
//    (FC3/uplay modules only), and the real function's return value. Pass-through.
//  * A poller thread scans new modules every 2 s and logs when uplay_r14 appears.
//
// Log file: <game bin>\orbit.log. Build: build.bat (MSVC x86 /MT).
// Safety: reads guarded with SEH; original d3d9.dll loaded from %SystemRoot%
// (full path) so our proxy can never recurse into itself.

#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <tlhelp32.h>
#include <psapi.h>
#include <stdio.h>
#include <stdarg.h>
#include <string.h>
#include <intrin.h>

#pragma comment(lib, "psapi.lib")

// ---------------------------------------------------------------- logging ---
static CRITICAL_SECTION g_cs;
static FILE* g_log = NULL;
static volatile LONG g_seq = 0;
static char g_exe_name[64] = "FC3.exe";

static void logOpen(void) {
    if (g_log) return;
    InitializeCriticalSection(&g_cs);
    char base[MAX_PATH]; GetModuleFileNameA(NULL, base, MAX_PATH);
    char* s = strrchr(base, '\\'); if (s) *s = 0;
    char path[MAX_PATH]; snprintf(path, MAX_PATH, "%s\\orbit.log", base);
    g_log = fopen(path, "a");
    if (g_log) { fprintf(g_log, "\n===== orbit_shim attach pid=%u =====\n", GetCurrentProcessId()); fflush(g_log); }
}
static void logFmt(const char* fmt, ...) {
    if (!g_log) return;
    EnterCriticalSection(&g_cs);
    SYSTEMTIME st; GetLocalTime(&st);
    fprintf(g_log, "[%02d:%02d:%02d.%03d] t%u #%lu ", st.wHour, st.wMinute, st.wSecond, st.wMilliseconds,
            GetCurrentThreadId(), (unsigned long)InterlockedIncrement(&g_seq));
    va_list ap; va_start(ap, fmt); vfprintf(g_log, fmt, ap); va_end(ap);
    fprintf(g_log, "\n");
    if (g_seq % 8 == 0) fflush(g_log);
    LeaveCriticalSection(&g_cs);
}

// -------------------------------------------- module description helpers ----
static HMODULE modOf(DWORD addr) {
    HMODULE h = NULL;
    if (!addr) return NULL;
    __try {
        if (!GetModuleHandleExA(GET_MODULE_HANDLE_EX_FLAG_FROM_ADDRESS | GET_MODULE_HANDLE_EX_FLAG_UNCHANGED_REFCOUNT,
                                (LPCSTR)addr, &h)) return NULL;
    } __except (EXCEPTION_EXECUTE_HANDLER) { return NULL; }
    return h;
}
static BOOL moduleName(HMODULE h, char* out, size_t cb) {
    char path[MAX_PATH] = {0};
    __try {
        if (GetModuleFileNameA(h, path, MAX_PATH)) { char* b = strrchr(path, '\\'); snprintf(out, cb, "%s", b ? b + 1 : path); return TRUE; }
    } __except (EXCEPTION_EXECUTE_HANDLER) {}
    snprintf(out, cb, "?"); return FALSE;
}
static void describe(DWORD addr, char* out, size_t cb) {
    out[0] = 0;
    HMODULE h = modOf(addr);
    if (!h) { snprintf(out, cb, "0x%x", addr); return; }
    char nm[64]; moduleName(h, nm, sizeof(nm));
    DWORD rva = addr - (DWORD)h;
    char tag[96] = {0};
    if (_stricmp(nm, g_exe_name) == 0 || strstr(nm, "FC3")) {
        if      (rva == 0x00cf6790) strcpy(tag, " [RVCreateGameSession]");
        else if (rva == 0x00cf6690) strcpy(tag, " [RVJoinGameSession]");
        else if (rva >= 0x010620400u && rva < 0x010623500u) strcpy(tag, " [UPLAY-party-glue-region]");
        else if (rva == 0x0113409d0) strcpy(tag, " [LOADER-FUN_113409d0]");
    }
    snprintf(out, cb, "%s+0x%x%s", nm, rva, tag);
}
static BOOL interestingModule(HMODULE h) {
    char nm[64]; if (!moduleName(h, nm, sizeof(nm))) return FALSE;
    return strstr(nm, "FC3") || _stricmp(nm, g_exe_name) == 0 || strstr(nm, "uplay") ||
           strstr(nm, "upc_") || strstr(nm, "RendezVous") || strstr(nm, "orbit") || strstr(nm, "Orbit");
}

// -------------------------------------------------- orbit real-pointer ------
typedef int  (__cdecl *fn_orbit_real)(DWORD interfaceId,
        DWORD a0, DWORD a1, DWORD a2, DWORD a3, DWORD a4, DWORD a5,
        DWORD a6, DWORD a7, DWORD a8, DWORD a9, DWORD a10, DWORD a11);
static volatile fn_orbit_real g_real_orbit = NULL;   // the REAL OrbitApi_InterfaceRequest
static HMODULE                g_real_orbit_mod = NULL;
static char  g_req_site_desc[160] = {0};              // who first asked for it

static fn_orbit_real findRealOrbitExport(void) {
    DWORD snap = CreateToolhelp32Snapshot(TH32CS_SNAPMODULE | TH32CS_SNAPMODULE32, GetCurrentProcessId());
    if (snap == INVALID_HANDLE_VALUE) return NULL;
    MODULEENTRY32W me; me.dwSize = sizeof(me);
    fn_orbit_real res = NULL; HMODULE resmod = NULL;
    if (Module32FirstW(snap, &me)) {
        do {
            HMODULE m = me.hModule;
            BYTE* img = (BYTE*)m;
            PIMAGE_DOS_HEADER dos; PIMAGE_NT_HEADERS nt; PIMAGE_EXPORT_DIRECTORY ex;
            __try {
                dos = (PIMAGE_DOS_HEADER)img;
                if (dos->e_magic != IMAGE_DOS_SIGNATURE) continue;
                nt = (PIMAGE_NT_HEADERS)(img + dos->e_lfanew);
                if (nt->Signature != IMAGE_NT_SIGNATURE) continue;
                DWORD rva = nt->OptionalHeader.DataDirectory[IMAGE_DIRECTORY_ENTRY_EXPORT].VirtualAddress;
                if (!rva) continue;
                ex = (PIMAGE_EXPORT_DIRECTORY)(img + rva);
                DWORD* names = (DWORD*)(img + ex->AddressOfNames);
                for (DWORD i = 0; i < ex->NumberOfNames; i++) {
                    const char* nm = (const char*)(img + names[i]);
                    if (strcmp(nm, "OrbitApi_InterfaceRequest") == 0) {
                        WORD* ords = (WORD*)(img + ex->AddressOfNameOrdinals);
                        DWORD* funcs = (DWORD*)(img + ex->AddressOfFunctions);
                        res = (fn_orbit_real)(img + funcs[ords[i]]);
                        resmod = m;
                        break;
                    }
                }
            } __except (EXCEPTION_EXECUTE_HANDLER) { continue; }
            if (res) break;
        } while (Module32NextW(snap, &me));
    }
    CloseHandle(snap);
    if (res) { g_real_orbit_mod = resmod; }
    return res;
}

// ------------------------------------------------------- the wrapper --------
static int __cdecl orbitLogged(DWORD interfaceId, ...) {
    va_list ap; va_start(ap, interfaceId);
    DWORD a[12]; for (int i = 0; i < 12; i++) a[i] = va_arg(ap, DWORD);
    va_end(ap);
    DWORD retaddr = (DWORD)_ReturnAddress();
    char d[170]; describe(retaddr, d, sizeof(d));
    logFmt("ORBIT-CALL id=%d | from %s | req-site %s", interfaceId, d, g_req_site_desc);
    logFmt("   args %08x %08x %08x %08x %08x %08x | %08x %08x %08x %08x %08x %08x",
           a[0], a[1], a[2], a[3], a[4], a[5], a[6], a[7], a[8], a[9], a[10], a[11]);
    // stack scan: first 240 DWORDs above our frame, print plausible code addrs in interesting modules
    {
        DWORD* sp = (DWORD*)&interfaceId;
        int found = 0;
        __try {
            for (int i = 12; i < 252 && found < 12; i++) {
                DWORD v = sp[i];
                HMODULE h = modOf(v);
                if (h && interestingModule(h)) {
                    char d2[170]; describe(v, d2, sizeof(d2));
                    logFmt("   stk+0x%x %s", i * 4, d2);
                    found++;
                }
            }
        } __except (EXCEPTION_EXECUTE_HANDLER) { logFmt("   (stack scan fault)"); }
    }
    int ret = -1;
    fn_orbit_real real = (fn_orbit_real)g_real_orbit;
    if (real) {
        __try {
            ret = real(interfaceId, a[0], a[1], a[2], a[3], a[4], a[5], a[6], a[7], a[8], a[9], a[10], a[11]);
        } __except (EXCEPTION_EXECUTE_HANDLER) { logFmt("ORBIT-CALL id=%d FAULT in real call", interfaceId); return -1; }
    } else {
        logFmt("ORBIT-CALL id=%d NO-REAL-POINTER returning -1", interfaceId);
    }
    logFmt("ORBIT-CALL id=%d ret=%d (0x%x)", interfaceId, ret, ret);
    return ret;
}

// ------------------------------------------------- GetProcAddress hooks -----
typedef FARPROC (WINAPI *fn_GPA)(HMODULE, LPCSTR);
static fn_GPA g_gpa_orig = NULL;      // pointer to the true kernel32 entry (from our own GetProcAddress, unhooked for us)

static FARPROC WINAPI gpaHook(HMODULE hMod, LPCSTR name) {
    FARPROC p = g_gpa_orig ? g_gpa_orig(hMod, name) : NULL;
    if (name && (UINT_PTR)name > 0xFFFF && strcmp(name, "OrbitApi_InterfaceRequest") == 0) {
        DWORD retaddr = (DWORD)_ReturnAddress();
        char d[170]; describe(retaddr, d, sizeof(d));
        char md[64]; if (hMod) moduleName(hMod, md, sizeof(md)); else strcpy(md, "?");
        logFmt("GETPROC(\"OrbitApi_InterfaceRequest\") module=%s from %s", md, d);
        snprintf(g_req_site_desc, sizeof(g_req_site_desc), "%s", d);
        if (!g_real_orbit) {
            fn_orbit_real r = findRealOrbitExport();
            if (r) {
                g_real_orbit = r;
                char rd[170]; describe((DWORD)r, rd, sizeof(rd));
                logFmt("   real export resolved: %s", rd);
            } else {
                logFmt("   real export NOT FOUND yet (uplay not loaded?) - wrapper will retry-fail until found");
            }
        }
        return (FARPROC)&orbitLogged;
    }
    return p;
}

// --------------------------------------------------- IAT scanner ------------
static int patchImportsOf(HMODULE mod) {
    int patched = 0;
    BYTE* img = (BYTE*)mod;
    PIMAGE_DOS_HEADER dos; PIMAGE_NT_HEADERS nt;
    __try {
        dos = (PIMAGE_DOS_HEADER)img;
        if (dos->e_magic != IMAGE_DOS_SIGNATURE) return 0;
        nt = (PIMAGE_NT_HEADERS)(img + dos->e_lfanew);
        if (nt->Signature != IMAGE_NT_SIGNATURE) return 0;
        DWORD rva = nt->OptionalHeader.DataDirectory[IMAGE_DIRECTORY_ENTRY_IMPORT].VirtualAddress;
        if (!rva) return 0;
        PIMAGE_IMPORT_DESCRIPTOR imp = (PIMAGE_IMPORT_DESCRIPTOR)(img + rva);
        for (; imp->Name; imp++) {
            const char* dn = (const char*)(img + imp->Name);
            if (_stricmp(dn, "kernel32.dll") != 0) continue;
            HMODULE k32 = GetModuleHandleA("kernel32.dll");
            void* tgtGPA  = (void*)GetProcAddress(k32, "GetProcAddress");
            void* tgtGPAa = (void*)GetProcAddress(k32, "GetProcAddressForANSIString");
            PIMAGE_THUNK_DATA thunk = (PIMAGE_THUNK_DATA)(img + imp->FirstThunk);
            PIMAGE_THUNK_DATA orig = imp->OriginalFirstThunk ? (PIMAGE_THUNK_DATA)(img + imp->OriginalFirstThunk) : NULL;
            for (int i = 0; thunk[i].u1.Function; i++) {
                void* cur = (void*)thunk[i].u1.Function;
                if (cur != tgtGPA && cur != tgtGPAa) continue;
                // confirm by name when available
                BOOL nameOk = FALSE;
                if (orig && !(orig[i].u1.Ordinal & IMAGE_ORDINAL_FLAG32)) {
                    PIMAGE_IMPORT_BY_NAME ibn = (PIMAGE_IMPORT_BY_NAME)(img + orig[i].u1.AddressOfData);
                    const char* fn = (const char*)ibn->Name;
                    nameOk = (strcmp(fn, "GetProcAddress") == 0 || strcmp(fn, "GetProcAddressForANSIString") == 0);
                }
                if (!nameOk && !tgtGPAa) continue; // unknown ordinal and no ANSI variant: skip cautiously
                DWORD old;
                if (VirtualProtect(&thunk[i].u1.Function, 4, PAGE_READWRITE, &old)) {
                    thunk[i].u1.Function = (DWORD_PTR)&gpaHook;
                    VirtualProtect(&thunk[i].u1.Function, 4, old, &old);
                    patched++;
                }
            }
        }
    } __except (EXCEPTION_EXECUTE_HANDLER) { return patched; }
    return patched;
}

static HMODULE g_scanned[192];
static int g_nscanned = 0;

static void scanOnce(const char* why) {
    DWORD snap = CreateToolhelp32Snapshot(TH32CS_SNAPMODULE | TH32CS_SNAPMODULE32, GetCurrentProcessId());
    if (snap == INVALID_HANDLE_VALUE) return;
    MODULEENTRY32W me; me.dwSize = sizeof(me);
    int total = 0;
    if (Module32FirstW(snap, &me)) {
        do {
            HMODULE m = me.hModule;
            int seen = 0;
            for (int i = 0; i < g_nscanned; i++) if (g_scanned[i] == m) { seen = 1; break; }
            if (seen) continue;
            if (g_nscanned < 192) g_scanned[g_nscanned++] = m;
            int n = patchImportsOf(m);
            if (n > 0) {
                char nm[64]; moduleName(m, nm, sizeof(nm));
                total += n;
            }
            (void)why;
        } while (Module32NextW(snap, &me));
    }
    CloseHandle(snap);
    if (total) logFmt("IAT scan (%s): patched %d GetProcAddress import slots", why, total);
}

static DWORD WINAPI poller(LPVOID p) {
    (void)p;
    Sleep(150); scanOnce("startup");
    int announced_uplay = 0;
    for (;;) {
        scanOnce("poll");
        if (!announced_uplay) {
            HMODULE h = GetModuleHandleA("uplay_r14.dll");
            if (!h) h = GetModuleHandleA("uplay_r2.dll");
            if (h) {
                announced_uplay = 1;
                char d[170]; describe((DWORD)h, d, sizeof(d));
                logFmt("uplay module up: %s", d);
                // announce the real export RVA as soon as present (independent of GetProcAddress flow)
                if (!g_real_orbit) {
                    fn_orbit_real r = findRealOrbitExport();
                    if (r) { g_real_orbit = r; char rd[170]; describe((DWORD)r, rd, sizeof(rd));
                             logFmt("pre-resolved real export: %s", rd); }
                }
            }
        }
        EnterCriticalSection(&g_cs); if (g_log) fflush(g_log); LeaveCriticalSection(&g_cs);
        Sleep(2000);
    }
    return 0;
}

// ------------------------------------------------ d3d9 proxy pass-through ---
static HMODULE g_real_d3d9 = NULL;
typedef HRESULT (WINAPI *fnD3DC9)(UINT);

__declspec(dllexport) HRESULT WINAPI Direct3DCreate9(UINT SDKVersion) {
    fnD3DC9 f = (fnD3DC9)GetProcAddress(g_real_d3d9, "Direct3DCreate9");
    return f ? f(SDKVersion) : E_NOTIMPL;
}
__declspec(dllexport) int WINAPI D3DPERF_SetOptions(DWORD o) {
    typedef int (WINAPI *fn)(DWORD);
    fn f = (fn)GetProcAddress(g_real_d3d9, "D3DPERF_SetOptions");
    return f ? f(o) : 0;
}
__declspec(dllexport) BOOL WINAPI D3DPERF_GetStatus(void) {
    typedef BOOL (WINAPI *fn)(void);
    fn f = (fn)GetProcAddress(g_real_d3d9, "D3DPERF_GetStatus");
    return f ? f() : FALSE;
}

// --------------------------------------------------------------- DllMain ----
BOOL WINAPI DllMain(HINSTANCE hinst, DWORD reason, LPVOID reserved) {
    (void)hinst; (void)reserved;
    if (reason == DLL_PROCESS_ATTACH) {
        DisableThreadLibraryCalls(hinst);
        logOpen();
        char exe[MAX_PATH]; GetModuleFileNameA(NULL, exe, MAX_PATH);
        char* b = strrchr(exe, '\\'); if (b) strcpy(g_exe_name, b + 1);
        // load the REAL d3d9.dll from the system directory (full path: no recursion)
        char sysdir[MAX_PATH]; GetSystemDirectoryA(sysdir, MAX_PATH);
        char real[MAX_PATH]; snprintf(real, MAX_PATH, "%s\\d3d9.dll", sysdir);
        g_real_d3d9 = LoadLibraryA(real);
        if (!g_real_d3d9) g_real_d3d9 = LoadLibraryExA(real, NULL, LOAD_LIBRARY_SEARCH_SYSTEM32);
        g_gpa_orig = (fn_GPA)GetProcAddress(GetModuleHandleA("kernel32.dll"), "GetProcAddress");
        logFmt("shim up: exe=%s real d3d9=%p", g_exe_name, g_real_d3d9);
        scanOnce("attach");   // patch FC3.exe + already-mapped static imports NOW
        CreateThread(NULL, 0, poller, NULL, 0, NULL);
    }
    return TRUE;
}
