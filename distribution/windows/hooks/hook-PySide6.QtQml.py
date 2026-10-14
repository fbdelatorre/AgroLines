# Widgets + QWebEngineView use no deployed QML interface. Keep QtQml's native
# dependency analysis, translations and tooling, without global QML discovery.
from PyInstaller.utils.hooks.qt import add_qt6_dependencies

from distribution.qt_payload import filter_collected

hiddenimports, binaries, datas = add_qt6_dependencies(__file__)
binaries = filter_collected(binaries)
datas = filter_collected(datas)
