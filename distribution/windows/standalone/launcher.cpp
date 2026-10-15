// Stable, offline-only process launcher. No GIS/application implementation here.
#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <shellapi.h>
#include <sddl.h>
#include <string>
#include <vector>

static constexpr wchar_t RunningMutex[] = L"Global\\AgroLinesStandalone-942C9844-703C-4B75-BE59-A66F3C3D9847";

static std::wstring quote(const std::wstring& argument) {
    std::wstring result = L"\"";
    size_t slashes = 0;
    for (wchar_t c : argument) {
        if (c == L'\\') { ++slashes; continue; }
        result.append(slashes * (c == L'\"' ? 2 : 1), L'\\');
        slashes = 0;
        if (c == L'\"') result += L'\\';
        result += c;
    }
    result.append(slashes * 2, L'\\');
    return result + L'\"';
}

static bool version_name(const std::string& text) {
    const size_t dash = text.find('-');
    if (dash == std::string::npos || text.size() - dash - 1 != 12) return false;
    int parts = 0;
    unsigned value = 0;
    bool digit = false;
    for (size_t i = 0; i <= dash; ++i) {
        char c = text[i];
        if (c >= '0' && c <= '9') {
            value = value * 10 + static_cast<unsigned>(c - '0');
            if (value > 65535) return false;
            digit = true;
        } else if (c == '.' || i == dash) {
            if (!digit) return false;
            ++parts; value = 0; digit = false;
        } else return false;
    }
    if (parts != 4) return false;
    for (size_t i = dash + 1; i < text.size(); ++i)
        if (!((text[i] >= '0' && text[i] <= '9') || (text[i] >= 'a' && text[i] <= 'f'))) return false;
    return true;
}

static bool plain_path(const std::wstring& path, bool directory) {
    const DWORD flags = GetFileAttributesW(path.c_str());
    return flags != INVALID_FILE_ATTRIBUTES && !(flags & FILE_ATTRIBUTE_REPARSE_POINT)
        && (((flags & FILE_ATTRIBUTE_DIRECTORY) != 0) == directory);
}

int WINAPI wWinMain(HINSTANCE, HINSTANCE, PWSTR, int) {
    std::vector<wchar_t> module(32768);
    DWORD count = GetModuleFileNameW(nullptr, module.data(), static_cast<DWORD>(module.size()));
    if (!count || count >= module.size()) return 2;
    std::wstring root(module.data(), count);
    root.resize(root.find_last_of(L"\\/"));
    const auto pointer = root + L"\\AgroLines.current.txt";
    if (!plain_path(root, true) || !plain_path(pointer, false)) return 3;
    HANDLE file = CreateFileW(pointer.c_str(), GENERIC_READ, FILE_SHARE_READ, nullptr,
                              OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL, nullptr);
    if (file == INVALID_HANDLE_VALUE) return 4;
    char bytes[128]{};
    DWORD read = 0;
    const bool okay = GetFileSize(file, nullptr) < sizeof(bytes)
        && ReadFile(file, bytes, sizeof(bytes), &read, nullptr);
    CloseHandle(file);
    std::string version(bytes, read);
    while (!version.empty() && (version.back() == '\r' || version.back() == '\n')) version.pop_back();
    if (!okay || !version_name(version)) return 5;
    const auto versions = root + L"\\versions";
    const auto selected = versions + L"\\" + std::wstring(version.begin(), version.end());
    const auto target = selected + L"\\AgroLines.exe";
    if (!plain_path(versions, true) || !plain_path(selected, true) || !plain_path(target, false)) return 6;
    int argc = 0;
    LPWSTR* argv = CommandLineToArgvW(GetCommandLineW(), &argc);
    if (!argv) return 7;
    std::wstring command = quote(target);
    for (int i = 1; i < argc; ++i) command += L" " + quote(argv[i]);
    LocalFree(argv);
    PSECURITY_DESCRIPTOR descriptor = nullptr;
    // Other authenticated Windows users may hold a synchronization handle only.
    if (!ConvertStringSecurityDescriptorToSecurityDescriptorW(
        L"D:(A;;GA;;;SY)(A;;GA;;;BA)(A;;0x00100000;;;AU)", SDDL_REVISION_1, &descriptor, nullptr)) return 8;
    SECURITY_ATTRIBUTES security{sizeof(SECURITY_ATTRIBUTES), descriptor, TRUE};
    HANDLE mutex = CreateMutexW(&security, FALSE, RunningMutex);
    if (!mutex && GetLastError() == ERROR_ACCESS_DENIED)
        mutex = OpenMutexW(SYNCHRONIZE, TRUE, RunningMutex);
    LocalFree(descriptor);
    if (!mutex) return 9;
    STARTUPINFOW startup{};
    startup.cb = sizeof(startup);
    startup.dwFlags = STARTF_TITLEISAPPID;
    startup.lpTitle = const_cast<LPWSTR>(L"Delatorre.AgroLines.Standalone");
    PROCESS_INFORMATION process{};
    const BOOL started = CreateProcessW(target.c_str(), command.data(), nullptr, nullptr, TRUE,
        CREATE_UNICODE_ENVIRONMENT, nullptr, selected.c_str(), &startup, &process);
    if (!started) {
        CloseHandle(mutex);
        MessageBoxW(nullptr, L"Não foi possível abrir o AgroLines. Consulte o suporte; não desative proteções do Windows.",
                    L"AgroLines", MB_OK | MB_ICONERROR);
        return 10;
    }
    CloseHandle(process.hThread);
    WaitForSingleObject(process.hProcess, INFINITE);
    DWORD exitCode = 1;
    GetExitCodeProcess(process.hProcess, &exitCode);
    CloseHandle(process.hProcess);
    CloseHandle(mutex);
    return static_cast<int>(exitCode);
}
