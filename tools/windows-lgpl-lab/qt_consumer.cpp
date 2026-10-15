// Synthetic consumer only. SPDX-License-Identifier: 0BSD
#include <QtCore/QString>
#include <QtCore/qglobal.h>
#include <windows.h>
#include <filesystem>
#include <iostream>
int main() {
    const QString value = QStringLiteral("talhao-sintetico");
    wchar_t path[32768];
    auto module = GetModuleHandleW(L"Qt6Core.dll");
    if (!module || !GetModuleFileNameW(module, path, 32768) || value.size() != 16) return 2;
    std::cout << "{\"version\":\"" << qVersion() << "\",\"length\":" << value.size()
              << ",\"loaded_path\":\"" << std::filesystem::path(path).generic_string() << "\"}";
}
