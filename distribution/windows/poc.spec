# Windows builder only. Onedir + no UPX: every native executable remains auditable.
from pathlib import Path
from PyInstaller.utils.hooks import collect_data_files

root = Path(SPECPATH).parent.parent
prepared = root / 'build' / 'distribution'
a = Analysis(
    [str(root / 'distribution/poc.py')],
    pathex=[str(root)],
    binaries=[],
    datas=[
        (str(root / 'desktop/map_assets'), 'desktop/map_assets'),
        (str(root / 'distribution/windows/brand.svg'), 'distribution/windows'),
        (str(prepared / 'metadata.json'), 'distribution/windows'),
        (str(root / 'distribution/windows/msix/identity.json'), 'distribution/windows/msix'),
    ] + collect_data_files('pyproj') + collect_data_files('fiona'),
    hiddenimports=[],
    hookspath=[],
    runtime_hooks=[],
    excludes=['PyQt5', 'PyQt6', 'PySide2', 'tkinter'],
    noarchive=False,
)
pyz = PYZ(a.pure)
exe = EXE(
    pyz, a.scripts, [], exclude_binaries=True, name='AgroLinesPoC',
    debug=False, strip=False, upx=False, console=False,
    icon=str(prepared / 'AgroLines.ico'), version=str(prepared / 'version.txt'),
)
coll = COLLECT(exe, a.binaries, a.datas, strip=False, upx=False, name='AgroLinesPoC')
