/*
 * fc3coop_probe.c -- dinput8.dll proxy + co-op session-id "poke" thread (H1 probe).
 *
 * Purpose
 *   Far Cry 3's engine DLL (FC3.dll / FC3_d3d11.dll) imports dinput8.dll. A proxy
 *   dinput8.dll placed next to the game executable is therefore loaded very early,
 *   which gives us a code-injection point without touching the game binary.
 *
 *   The proxy must be invisible to the game, so it forwards all six exports of the
 *   real dinput8.dll (names + ordinals 1..6) to the genuine system copy, which is
 *   loaded by FULL PATH from GetSystemDirectory() to avoid the self-load name
 *   collision (our file is also called dinput8.dll).
 *
 *   On top of forwarding, a background thread runs the H1 experiment: it locates the
 *   live engine base at runtime (FC3.dll is ASLR-enabled, preferred base 0x10000000)
 *   and continuously writes the co-op session id 0x43521E6F into two engine globals.
 *   Continuous re-poking is intentional (single-write timing is unknown), so every
 *   write is guarded so a wrong/unclicked pointer can never crash the game.
 *
 * Build: 32-bit MSVC, static CRT. See build.bat. Do NOT build x64.
 *
 * This file is self-contained C (no DirectX headers required).
 */

/* Exports come from dinput8.def ONLY (names + ordinals 1..6). No __declspec(dllexport):
 * with stdcall it would additionally publish decorated names like _DirectInput8Create@20,
 * and the real dinput8.dll exports exactly six undecorated names. */
#define _CRT_SECURE_NO_WARNINGS
#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <excpt.h>
#include <stdio.h>
#include <string.h>

/* ------------------------------------------------------------------ *
 * H1 experiment constants (verified against FC3 1.06, x86)
 * ------------------------------------------------------------------ */
#define FC3_PREFERRED_BASE 0x10000000u /* ASLR is ON: not the live base, do not use it */

/* RVAs (VA - 0x10000000) of the two co-op session-id globals. */
#define FC3_G1_RVA 0x02891CA0u
#define FC3_G2_RVA 0x02891CA8u

/* The co-op session id to force into both globals (little-endian uint32). */
#define FC3_COOP_ID 0x43521E6Fu

/* Engine module names to look for (d3d9 renderer / d3d11 renderer variant). */
#define FC3_MODNAME L"FC3.dll"
#define FC3_MODNAME_DX11 L"FC3_d3d11.dll"

#define POLL_BASE_MS 200u /* how often to look for the engine base */
#define POKE_MS 500u      /* how often to re-poke the globals */
#define LOG_MAX_WRITES 5  /* never log more than the first N writes */

/* ------------------------------------------------------------------ *
 * Module state
 * ------------------------------------------------------------------ */
static HMODULE g_self = NULL; /* our own dinput8.dll */

/* ------------------------------------------------------------------ *
 * Forwarding to the real dinput8.dll
 *
 * Real dinput8.dll (x86) exports exactly six functions, all __stdcall:
 *   1 DirectInput8Create  (HINSTANCE, DWORD, REFIID, LPVOID*, LPUNKNOWN)  20 bytes
 *   2 DllCanUnloadNow     ()                                               0 bytes
 *   3 DllGetClassObject   (REFCLSID, REFIID, LPVOID*)                     12 bytes
 *   4 DllRegisterServer   ()                                               0 bytes
 *   5 DllUnregisterServer ()                                               0 bytes
 *   6 GetdfDIJoystick     ()                                               0 bytes
 * The arities above are load-bearing: the stubs are __stdcall, so a wrong byte
 * count would corrupt the caller's stack. Direct pointers are declared as void*
 * because we only pass them through and do not want a DirectX-header dependency.
 * ------------------------------------------------------------------ */
#define E_FWD_FAIL ((HRESULT)0x80004005L) /* E_FAIL: forward target unavailable */

typedef HRESULT(WINAPI *PFN_DirectInput8Create)(HINSTANCE hinst,
                                                DWORD dwVersion,
                                                const void *riidltf,
                                                void **ppvOut,
                                                void *punkOuter);
typedef HRESULT(WINAPI *PFN_DllCanUnloadNow)(void);
typedef HRESULT(WINAPI *PFN_DllGetClassObject)(const void *rclsid,
                                               const void *riid,
                                               void **ppv);
typedef HRESULT(WINAPI *PFN_DllRegisterServer)(void);
typedef HRESULT(WINAPI *PFN_DllUnregisterServer)(void);
typedef HRESULT(WINAPI *PFN_GetdfDIJoystick)(void);

static volatile LONG g_fwd_state = 0; /* 0 = not started, 2 = done */
static HMODULE g_real = NULL;
static PFN_DirectInput8Create pDirectInput8Create = NULL;
static PFN_DllCanUnloadNow pDllCanUnloadNow = NULL;
static PFN_DllGetClassObject pDllGetClassObject = NULL;
static PFN_DllRegisterServer pDllRegisterServer = NULL;
static PFN_DllUnregisterServer pDllUnregisterServer = NULL;
static PFN_GetdfDIJoystick pGetdfDIJoystick = NULL;

/* Resolve by name, falling back to the known ordinal. */
static FARPROC fwd_get(const char *name, DWORD ordinal) {
    FARPROC p = GetProcAddress(g_real, name);
    if (p == NULL && ordinal >= 1 && ordinal <= 6) {
        p = GetProcAddress(g_real, (LPCSTR)(UINT_PTR)ordinal);
    }
    return p;
}

/*
 * Lazy one-time load of the genuine dinput8.dll.
 * Done lazily on the first forwarded call, NOT in DllMain: LoadLibrary from
 * DllMain runs under the loader lock and is a documented deadlock risk.
 */
static void fwd_init(void) {
    LONG st;

    if (g_fwd_state != 0) {
        return;
    }
    if (InterlockedCompareExchange(&g_fwd_state, 1, 0) != 0) {
        /* Another thread is initializing; wait for it to finish. */
        for (;;) {
            st = g_fwd_state;
            if (st == 2) {
                return;
            }
            Sleep(1);
        }
    }

    {
        WCHAR path[MAX_PATH + 16];
        DWORD n = GetSystemDirectoryW(path, MAX_PATH);
        if (n == 0 || n >= MAX_PATH) {
            /* Fallback: bare name resolved through the default search order. */
            wcscpy(path, L"dinput8.dll");
        } else {
            wcscat(path, L"\\dinput8.dll");
        }

        /* Full path + altered search path = the copy in the system directory,
         * never this proxy DLL sitting next to the game executable. */
        g_real = LoadLibraryExW(path, NULL, LOAD_WITH_ALTERED_SEARCH_PATH);

        if (g_real != NULL) {
            pDirectInput8Create = (PFN_DirectInput8Create)fwd_get("DirectInput8Create", 1);
            pDllCanUnloadNow = (PFN_DllCanUnloadNow)fwd_get("DllCanUnloadNow", 2);
            pDllGetClassObject = (PFN_DllGetClassObject)fwd_get("DllGetClassObject", 3);
            pDllRegisterServer = (PFN_DllRegisterServer)fwd_get("DllRegisterServer", 4);
            pDllUnregisterServer = (PFN_DllUnregisterServer)fwd_get("DllUnregisterServer", 5);
            pGetdfDIJoystick = (PFN_GetdfDIJoystick)fwd_get("GetdfDIJoystick", 6);
        }
    }

    InterlockedExchange(&g_fwd_state, 2);
}

HRESULT WINAPI DirectInput8Create(HINSTANCE hinst,
                                                        DWORD dwVersion,
                                                        const void *riidltf,
                                                        void **ppvOut,
                                                        void *punkOuter) {
    fwd_init();
    if (pDirectInput8Create == NULL) {
        return E_FWD_FAIL;
    }
    return pDirectInput8Create(hinst, dwVersion, riidltf, ppvOut, punkOuter);
}

HRESULT WINAPI DllCanUnloadNow(void) {
    fwd_init();
    if (pDllCanUnloadNow == NULL) {
        return E_FWD_FAIL;
    }
    return pDllCanUnloadNow();
}

HRESULT WINAPI DllGetClassObject(const void *rclsid,
                                                       const void *riid,
                                                       void **ppv) {
    fwd_init();
    if (pDllGetClassObject == NULL) {
        return E_FWD_FAIL;
    }
    return pDllGetClassObject(rclsid, riid, ppv);
}

HRESULT WINAPI DllRegisterServer(void) {
    fwd_init();
    if (pDllRegisterServer == NULL) {
        return E_FWD_FAIL;
    }
    return pDllRegisterServer();
}

HRESULT WINAPI DllUnregisterServer(void) {
    fwd_init();
    if (pDllUnregisterServer == NULL) {
        return E_FWD_FAIL;
    }
    return pDllUnregisterServer();
}

HRESULT WINAPI GetdfDIJoystick(void) {
    fwd_init();
    if (pGetdfDIJoystick == NULL) {
        return E_FWD_FAIL;
    }
    return pGetdfDIJoystick();
}

/* ------------------------------------------------------------------ *
 * Logging: fc3coop_probe.log next to this DLL, so the owner can confirm
 * the probe actually ran. Append-only, shareable, never fatal.
 * ------------------------------------------------------------------ */
static void log_line(const WCHAR *fmt, ...) {
    WCHAR file[MAX_PATH * 2];
    WCHAR msg[512];
    va_list ap;
    HANDLE h;
    DWORD written;
    size_t len;

    if (g_self == NULL) {
        return;
    }
    if (GetModuleFileNameW(g_self, file, MAX_PATH) == 0) {
        return;
    }
    {
        WCHAR *slash = wcsrchr(file, L'\\');
        if (slash == NULL) {
            return;
        }
        slash[1] = L'\0';
        wcscat(file, L"fc3coop_probe.log");
    }

    va_start(ap, fmt);
    _vsnwprintf(msg, 480, fmt, ap);
    va_end(ap);
    msg[480] = L'\0';

    len = wcslen(msg);
    msg[len] = L'\r';
    msg[len + 1] = L'\n';
    msg[len + 2] = L'\0';

    h = CreateFileW(file, FILE_APPEND_DATA, FILE_SHARE_READ | FILE_SHARE_WRITE, NULL,
                    OPEN_ALWAYS, FILE_ATTRIBUTE_NORMAL, NULL);
    if (h == INVALID_HANDLE_VALUE) {
        return;
    }
    WriteFile(h, msg, (DWORD)(wcslen(msg) * sizeof(WCHAR)), &written, NULL);
    CloseHandle(h);
}

/* ------------------------------------------------------------------ *
 * Guarded write + engine discovery
 * ------------------------------------------------------------------ */

/* True if the page containing addr is committed and already writable. */
static int page_writable(uintptr_t addr) {
    MEMORY_BASIC_INFORMATION mbi;
    DWORD ok;

    if (VirtualQuery((LPCVOID)addr, &mbi, sizeof(mbi)) != sizeof(mbi)) {
        return 0;
    }
    if (mbi.State != MEM_COMMIT || mbi.AllocationBase == NULL) {
        return 0;
    }
    ok = mbi.Protect & (PAGE_READWRITE | PAGE_WRITECOPY | PAGE_EXECUTE_READWRITE |
                        PAGE_EXECUTE_WRITECOPY);
    return ok != 0;
}

/*
 * Write a uint32 to a live engine address, guarded twice:
 *   1. VirtualQuery must report a committed, writable page.
 *   2. The store itself runs inside SEH, so any surprise fault is swallowed.
 * VirtualProtect is used to force PAGE_READWRITE and the old protection is
 * restored afterwards, leaving the engine's memory layout untouched.
 * Returns 1 on success, 0 if the write was skipped.
 */
static int poke_u32(uintptr_t addr, unsigned value) {
    DWORD old = 0;
    DWORD dummy = 0;
    int changed = 0;

    if (!page_writable(addr)) {
        return 0;
    }
    if (!VirtualProtect((PVOID)addr, sizeof(unsigned), PAGE_READWRITE, &old)) {
        return 0;
    }
    changed = 1;

    __try {
        *(volatile unsigned *)addr = value;
    }
    __except (EXCEPTION_EXECUTE_HANDLER) {
        changed = 0;
    }

    if (changed) {
        /* Restore the original protection (it may already be PAGE_READWRITE). */
        VirtualProtect((PVOID)addr, sizeof(unsigned), old, &dummy);
    }
    return changed;
}

/*
 * Read a uint32 from a live engine address, guarded twice (VirtualQuery for a
 * committed, readable page + SEH around the load). Returns 1 and writes *out on
 * success, 0 if the address is not safely readable. Used to observe the engine's
 * own value at the co-op globals (pre-poke default, and post-poke read-back).
 */
static int peek_u32(uintptr_t addr, unsigned *out) {
    MEMORY_BASIC_INFORMATION mbi;

    if (VirtualQuery((LPCVOID)addr, &mbi, sizeof(mbi)) != sizeof(mbi)) {
        return 0;
    }
    if (mbi.State != MEM_COMMIT) {
        return 0;
    }
    if (!(mbi.Protect & (PAGE_READONLY | PAGE_READWRITE | PAGE_WRITECOPY | PAGE_EXECUTE_READ |
                         PAGE_EXECUTE_READWRITE | PAGE_EXECUTE_WRITECOPY))) {
        return 0; /* PAGE_NOACCESS / guard / unknown: do not touch */
    }

    __try {
        *out = *(volatile unsigned *)addr;
    }
    __except (EXCEPTION_EXECUTE_HANDLER) {
        return 0;
    }
    return 1;
}

/* Locate the live engine image. Returns its runtime base, 0 when not loaded. */
static uintptr_t find_engine(const WCHAR **out_name) {
    HMODULE h = GetModuleHandleW(FC3_MODNAME);

    if (h != NULL) {
        *out_name = FC3_MODNAME;
        return (uintptr_t)h;
    }
    h = GetModuleHandleW(FC3_MODNAME_DX11);
    if (h != NULL) {
        *out_name = FC3_MODNAME_DX11;
        return (uintptr_t)h;
    }
    *out_name = NULL;
    return 0;
}

static DWORD WINAPI poke_thread(LPVOID arg) {
    uintptr_t base;
    const WCHAR *name;
    int logged_writes = 0;
    int logged_overwrite = 0;
    int pokes_done = 0;
    (void)arg;

    for (;;) {
        /* Phase 1: wait for the engine DLL to appear. */
        do {
            Sleep(POLL_BASE_MS);
            base = find_engine(&name);
        } while (base == 0);

        log_line(L"FC3 coop probe: engine base = 0x%08X (from %s)", (unsigned)base, name);

        /* Read the globals BEFORE writing them: this captures whatever value the engine
         * holds on its own (e.g. the single-player default), so one run of the probe
         * already tells us what a normal game stores at these two addresses. */
        {
            unsigned d1 = 0, d2 = 0;
            int r1 = peek_u32(base + FC3_G1_RVA, &d1);
            int r2 = peek_u32(base + FC3_G2_RVA, &d2);
            if (r1 && r2) {
                log_line(L"pre-poke default: [g1]=0x%08X [g2]=0x%08X", d1, d2);
            } else {
                log_line(L"pre-poke: g1_readable=%d g2_readable=%d (page not committed yet?)",
                         r1, r2);
            }
        }

        /* Phase 2: keep forcing the co-op id into both globals, and read the value back
         * right after each write. If the read-back differs from FC3_COOP_ID, the engine
         * overwrote us between the write and the read -- that is exactly the question
         * H1 must answer (can a poke stick at all, or is the real state elsewhere). */
        for (;;) {
            int ok1, ok2;
            unsigned b1 = 0, b2 = 0;

            Sleep(POKE_MS);

            /* If the engine went away, go back to polling for a new base. */
            if (GetModuleHandleW(name) == NULL) {
                break;
            }

            ok1 = poke_u32(base + FC3_G1_RVA, FC3_COOP_ID);
            ok2 = poke_u32(base + FC3_G2_RVA, FC3_COOP_ID);
            pokes_done++;

            (void)peek_u32(base + FC3_G1_RVA, &b1);
            (void)peek_u32(base + FC3_G2_RVA, &b2);

            if (logged_writes < LOG_MAX_WRITES) {
                logged_writes++;
                log_line(L"poke %d/%d: g1_ok=%d g2_ok=%d readback [g1]=0x%08X [g2]=0x%08X",
                         logged_writes, LOG_MAX_WRITES, ok1, ok2, b1, b2);
            } else if ((b1 != FC3_COOP_ID || b2 != FC3_COOP_ID) &&
                       logged_overwrite < LOG_MAX_WRITES) {
                logged_overwrite++;
                log_line(L"OVERWRITE: readback [g1]=0x%08X [g2]=0x%08X (wanted 0x%08X) pokes_done=%d",
                         b1, b2, FC3_COOP_ID, pokes_done);
            } else if (pokes_done % 20 == 0) {
                /* Heartbeat roughly every 10s so the log keeps showing the held value. */
                log_line(L"heartbeat poke #%d: [g1]=0x%08X [g2]=0x%08X", pokes_done, b1, b2);
            }
        }
    }

    return 0;
}

/* ------------------------------------------------------------------ *
 * DllMain
 * ------------------------------------------------------------------ */
static void on_attach(void) {
    HANDLE th;
    DWORD tid;

    th = CreateThread(NULL, 0, poke_thread, NULL, 0, &tid);
    if (th != NULL) {
        CloseHandle(th);
    }
}

BOOL WINAPI DllMain(HINSTANCE hinstDLL, DWORD fdwReason, LPVOID lpvReserved) {
    (void)lpvReserved;

    switch (fdwReason) {
    case DLL_PROCESS_ATTACH:
        g_self = hinstDLL;
        DisableThreadLibraryCalls(hinstDLL);
        on_attach();
        break;
    case DLL_PROCESS_DETACH:
        break;
    default:
        break;
    }
    return TRUE;
}
