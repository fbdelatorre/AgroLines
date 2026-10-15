// Synthetic LGPL experiment only; no AgroLines implementation. SPDX-License-Identifier: 0BSD
#include <QtCore/QString>
#include <QtCore/qglobal.h>
#include <iostream>
int main() {
    const QString value = QStringLiteral("talhao-sintetico");
    if (value.size() != 16) return 1;
    std::cout << "{\"version\":\"" << qVersion() << "\",\"length\":" << value.size() << "}";
}
