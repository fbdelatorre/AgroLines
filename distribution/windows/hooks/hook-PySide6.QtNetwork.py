from PyInstaller.utils.hooks.qt import add_qt6_dependencies

hiddenimports, binaries, datas = add_qt6_dependencies(__file__)
# The offline Windows application has no Qt HTTPS consumer. Preserve QtNetwork
# native dependencies and Windows Schannel, but do not collect an unused OpenSSL
# provider or discover arbitrary OpenSSL DLLs from MySQL/other tools on PATH.
binaries = [entry for entry in binaries if not entry[0].lower().endswith("qopensslbackend.dll")]
