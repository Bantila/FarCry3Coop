// proxytest.c - call a stub loader API directly; compare proxy forwarding vs the stub itself.
// Usage: proxytest <dll-path>   (writes stdout only; runs in ~seconds)
#include <windows.h>
#include <stdio.h>

typedef int (__cdecl *f_i0)(void);
typedef int (__cdecl *f_i1)(int);
typedef int (__cdecl *f_i3)(int, int, int);

static void dump(const char* tag, int r, void* p) {
    printf("%s ret=%d", tag, r);
    if (r > 0 && r < 0x7fff0000) {
        unsigned char* b = (unsigned char*)r;
        printf(" ->dword[0..15]:");
        int n = 0;
        __try { for (; n < 16; n++) printf(" %02X", b[n]); }
        __except (EXCEPTION_EXECUTE_HANDLER) { printf(" <fault@%d>", n); }
    }
    printf("\n");
    fflush(stdout);
}

int main(int argc, char** argv) {
    const char* dll = (argc > 1) ? argv[1] : "uplay_r1_loader.dll";
    printf("dll=%s\n", dll);
    fflush(stdout);
    HMODULE h = LoadLibraryA(dll);
    if (!h) { printf("LoadLibrary err=%lu\n", GetLastError()); return 2; }

    f_i1 Init = (f_i1)GetProcAddress(h, "UPLAY_Init");
    f_i1 PInit = (f_i1)GetProcAddress(h, "UPLAY_PARTY_Init");
    f_i0 IsConn = (f_i0)GetProcAddress(h, "UPLAY_USER_IsConnected");
    f_i0 InParty = (f_i0)GetProcAddress(h, "UPLAY_PARTY_IsInParty");
    f_i1 Poll = (f_i1)GetProcAddress(h, "UPLAY_Poll");
    printf("ptrs Init=%p PInit=%p IsConn=%p InParty=%p Poll=%p\n", Init, PInit, IsConn, InParty, Poll);
    fflush(stdout);

    printf("IsConnected BEFORE=%d\n", IsConn ? IsConn() : -999);
    static char blob[4096];
    if (Init) dump("Init", Init((int)(size_t)blob), 0);
    if (Poll) dump("Poll", Poll(0), 0);
    printf("IsConnected AFTER=%d\n", IsConn ? IsConn() : -999);
    if (PInit) dump("PARTY_Init", PInit(2), 0);
    printf("PARTY_IsInParty=%d\n", InParty ? InParty() : -999);
    if (Poll) dump("Poll2", Poll(0), 0);
    fflush(stdout);
    return 0;
}
