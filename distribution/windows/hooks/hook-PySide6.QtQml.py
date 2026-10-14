# Retain upstream module dependency/plugin analysis, but exclude the six unused
# families from QML discovery BEFORE PyInstaller expands their DLL dependencies.
from PyInstaller.utils.hooks.qt import add_qt6_dependencies, pyside6_library_info

from distribution.qt_payload import filter_collected

hiddenimports, binaries, datas = add_qt6_dependencies(__file__)
qml_binaries, qml_datas = pyside6_library_info.collect_qtqml_files()
binaries = filter_collected(binaries + qml_binaries)
datas = filter_collected(datas + qml_datas)
