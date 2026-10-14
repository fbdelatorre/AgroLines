# Windows builder only. Onedir + no UPX: every native executable remains auditable.
import json
from pathlib import Path
from PyInstaller.utils.hooks import collect_data_files
from distribution.build import privacy_assets
from distribution.qt_payload import PYTHON_EXCLUDES, record_analysis

root = Path(SPECPATH).parent.parent
prepared = root / 'build' / 'distribution'
store = json.loads((prepared / 'metadata.json').read_text()).get('offline_only') is True
remote = ['desktop.main', 'desktop.client', 'desktop.health', 'desktop.vault',
          'desktop.pages', 'desktop.geography', 'server', 'fastapi', 'uvicorn', 'psycopg']
a = Analysis(
    [str(root / ('distribution/store.py' if store else 'distribution/poc.py'))],
    pathex=[str(root)],
    binaries=[],
    datas=[
        (str(root / 'desktop/map_assets'), 'desktop/map_assets'),
        (str(prepared / 'AgroLines.ico'), 'distribution/windows'),
        (str(root / 'assets/branding/AgroLines_Arte_Caixa_1080x1080.png'), 'assets/branding'),
        (str(prepared / 'metadata.json'), 'distribution/windows'),
        (str(root / 'distribution/windows/msix/identity.json'), 'distribution/windows/msix'),
    ] + (privacy_assets() if store else [])
      + collect_data_files('pyproj') + collect_data_files('fiona'),
    hiddenimports=[],
    hookspath=[str(root / 'distribution/windows/hooks')],
    runtime_hooks=[str(root / 'distribution/windows/offline_hook.py')] if store else [],
    excludes=['PyQt5', 'PyQt6', 'PySide2', 'tkinter'] + PYTHON_EXCLUDES + (remote if store else []),
    noarchive=False,
)
record_analysis(a, root / 'evidence/qt-minimal/build-inputs.json')
if store and any(name == module or name.startswith(module + '.')
                 for name, _, _ in a.pure for module in remote):
    raise RuntimeError('Remote module leaked into offline Store payload')
pyz = PYZ(a.pure)
exe = EXE(
    pyz, a.scripts, [], exclude_binaries=True, name='AgroLinesPoC',
    debug=False, strip=False, upx=False, console=False,
    icon=str(prepared / 'AgroLines.ico'), version=str(prepared / 'version.txt'),
)
coll = COLLECT(exe, a.binaries, a.datas, strip=False, upx=False, name='AgroLinesPoC')
