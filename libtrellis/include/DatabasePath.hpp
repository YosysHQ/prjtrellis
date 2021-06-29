#ifndef LIBTRELLIS_DATABASEPATH_H
#define LIBTRELLIS_DATABASEPATH_H

#include <boost/version.hpp>
#include <boost/filesystem.hpp>

#if BOOST_VERSION >= 106100

#if defined(__wasm)

std::string get_database_path()
{
    return "/share/trellis/database";
}

#else

#include <boost/dll/runtime_symbol_info.hpp>

std::string get_database_path()
{
    boost::filesystem::path executable_path = boost::dll::program_location().parent_path();
    boost::filesystem::path database_datadir_relative(TRELLIS_RPATH_DATADIR "/" TRELLIS_PROGRAM_PREFIX "trellis/database");
    std::string database_folder = (executable_path /= database_datadir_relative).string();
    return database_folder;
}

#endif

#else

/*
 *  yosys -- Yosys Open SYnthesis Suite
 *
 *  Copyright (C) 2012  Claire Xenia Wolf <claire@yosyshq.com>
 *
 *  Permission to use, copy, modify, and/or distribute this software for any
 *  purpose with or without fee is hereby granted, provided that the above
 *  copyright notice and this permission notice appear in all copies.
 *
 *  THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
 *  WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
 *  MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
 *  ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
 *  WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
 *  ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
 *  OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
 *
 */

#include <errno.h>
#include <string>
#include <sstream>
#include <cstring>

#ifdef _WIN32
#  include <windows.h>
#  include <io.h>
#elif defined(__APPLE__)
#  include <mach-o/dyld.h>
#  include <unistd.h>
#else
#  include <unistd.h>
#endif

#ifdef __FreeBSD__
#  include <sys/sysctl.h>
#endif

#include <limits.h>

#if defined(__linux__) || defined(__CYGWIN__)
std::string proc_self_dirname()
{
    char path[PATH_MAX];
    ssize_t buflen = readlink("/proc/self/exe", path, sizeof(path));
    if (buflen < 0) {
        fprintf(stderr, "fatal error: readlink(\"/proc/self/exe\") failed: %s\n", strerror(errno));
        exit(EXIT_FAILURE);
    }
    while (buflen > 0 && path[buflen-1] != '/')
        buflen--;
    return std::string(path, buflen);
}
#elif defined(__FreeBSD__)
std::string proc_self_dirname()
{
    int mib[4] = {CTL_KERN, KERN_PROC, KERN_PROC_PATHNAME, -1};
    size_t buflen;
    char *buffer;
    std::string path;
    if (sysctl(mib, 4, NULL, &buflen, NULL, 0) != 0) {
        fprintf(stderr, "fatal error: sysctl failed: %s\n", strerror(errno));
        exit(EXIT_FAILURE);
    }
    buffer = (char*)malloc(buflen);
    if (buffer == NULL) {
        fprintf(stderr, "fatal error: malloc failed: %s\n", strerror(errno));
        exit(EXIT_FAILURE);
    }
    if (sysctl(mib, 4, buffer, &buflen, NULL, 0) != 0) {
        fprintf(stderr, "fatal error: sysctl failed: %s\n", strerror(errno));
        exit(EXIT_FAILURE);
    }
    while (buflen > 0 && buffer[buflen-1] != '/')
        buflen--;
    path.assign(buffer, buflen);
    free(buffer);
    return path;
}
#elif defined(__APPLE__)
std::string proc_self_dirname()
{
    char *path = NULL;
    uint32_t buflen = 0;
    while (_NSGetExecutablePath(path, &buflen) != 0)
        path = (char *) realloc((void *) path, buflen);
    while (buflen > 0 && path[buflen-1] != '/')
        buflen--;
    return std::string(path, buflen);
}
#elif defined(_WIN32)
std::string proc_self_dirname()
{
    int i = 0;
#  ifdef __MINGW32__
    char longpath[MAX_PATH + 1];
    char shortpath[MAX_PATH + 1];
#  else
    WCHAR longpath[MAX_PATH + 1];
    TCHAR shortpath[MAX_PATH + 1];
#  endif
    if (!GetModuleFileName(0, longpath, MAX_PATH+1)) {
        fprintf(stderr, "fatal error: GetModuleFileName() failed.\n");
        exit(EXIT_FAILURE);
    }
    if (!GetShortPathName(longpath, shortpath, MAX_PATH+1)) {
        fprintf(stderr, "fatal error: GetShortPathName() failed.\n");
        exit(EXIT_FAILURE);
    }
    while (shortpath[i] != 0)
        i++;
    while (i > 0 && shortpath[i-1] != '/' && shortpath[i-1] != '\\')
        shortpath[--i] = 0;
    std::string path;
    for (i = 0; shortpath[i]; i++)
        path += char(shortpath[i]);
    return path;
}
#elif defined(EMSCRIPTEN)
std::string proc_self_dirname()
{
    return "/";
}
#else
    #error Dont know how to determine process executable base path!
#endif

std::string get_database_path()
{
    boost::filesystem::path executable_path = boost::filesystem::path(proc_self_dirname()).parent_path();
    boost::filesystem::path database_datadir_relative(TRELLIS_RPATH_DATADIR "/trellis/database");
    std::string database_folder = (executable_path /= database_datadir_relative).string();
    return database_folder;
}

#endif

#endif //LIBTRELLIS_DATABASEPATH_HPP
