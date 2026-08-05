#ifdef _WIN32
#define WIN32_LEAN_AND_MEAN
#define NOMINMAX
#define NOGDI
#  include <windows.h>
#  include <shellapi.h>
#endif
#include "Util.hpp"

namespace Trellis {
VerbosityLevel verbosity = VerbosityLevel::DEBUG;

void use_utf8(int *argcp, char ***argvp) {
#ifdef _WIN32
    // Configure ASCII functions like fopen() to use UTF-8 filenames.
    // See https://learn.microsoft.com/en-us/cpp/c-runtime-library/reference/setlocale-wsetlocale?view=msvc-170#utf-8-support
#ifdef _UCRT
    setlocale(LC_ALL, ".UTF-8");
#endif
    // Configure the Win32 console to use UTF-8.
    SetConsoleCP(CP_UTF8);
    SetConsoleOutputCP(CP_UTF8);
    // Translate arguments to UTF-8.
    *argcp = 0;
    LPWSTR *wargv = CommandLineToArgvW(GetCommandLineW(), argcp);
    *argvp = (char**)malloc(sizeof(char*) * *argcp);
    for (int i = 0; i < *argcp; i++) {
        int usize = WideCharToMultiByte(CP_UTF8, 0, wargv[i], -1, NULL, 0, NULL, NULL);
        char *uarg = (char *)malloc(usize);
        WideCharToMultiByte(CP_UTF8, 0, wargv[i], -1, uarg, usize, NULL, NULL);
        (*argvp)[i] = uarg;
    }
    (*argvp)[*argcp] = NULL;
#else
    UNUSED(argcp);
    UNUSED(argvp);
#endif
}
}
