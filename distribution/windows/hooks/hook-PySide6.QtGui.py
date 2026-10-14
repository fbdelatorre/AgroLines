from PyInstaller.utils.hooks.qt import add_qt6_dependencies

from distribution.qt_payload import filter_collected

hiddenimports, binaries, datas = add_qt6_dependencies(__file__)
# Qt's automatic platforminputcontexts collection otherwise pulls VirtualKeyboard.
binaries = filter_collected(binaries)
datas = filter_collected(datas)
