# Windows builder only. Onedir + no UPX: every native executable remains auditable.
import json
from pathlib import Path
from PyInstaller.utils.hooks import collect_data_files
from distribution.build import privacy_assets
from distribution.qt_payload import PYTHON_EXCLUDES, assert_widget_deployment, omit_system_copies, record_analysis

root = Path(SPECPATH).parent.parent
prepared = root / 'build' / 'distribution'
metadata = json.loads((prepared / 'metadata.json').read_text())
# Both offline channels use the exact reviewed Qt hooks/exclusions and network policy.
store = metadata.get('offline_only') is True
standalone = metadata.get('distribution_channel') == 'standalone-offline'
name = 'AgroLines' if standalone else 'AgroLinesPoC'
if store:
    assert_widget_deployment(root)
remote = ['desktop.main', 'desktop.client', 'desktop.health', 'desktop.vault',
          'desktop.pages', 'desktop.geography', 'server', 'fastapi', 'uvicorn', 'psycopg']
a = Analysis(
    [str(root / ('distribution/standalone.py' if standalone else 'distribution/store.py' if store else 'distribution/poc.py'))],
    pathex=[str(root)],
    binaries=[],
    datas=[
        (str(root / 'desktop/map_assets'), 'desktop/map_assets'),
        (str(prepared / 'AgroLines.ico'), 'distribution/windows'),
        (str(root / 'assets/branding/AgroLines_Arte_Caixa_1080x1080.png'), 'assets/branding'),
        (str(prepared / 'metadata.json'), 'distribution/windows'),
    ] + ([(str(root / 'distribution/windows/msix/identity.json'), 'distribution/windows/msix')] if not standalone else [])
      + (privacy_assets(standalone=standalone) if store else [])
      + collect_data_files('pyproj') + collect_data_files('fiona'),
    hiddenimports=[],
    hookspath=[str(root / 'distribution/windows/hooks')] if store else [],
    runtime_hooks=[str(root / 'distribution/windows/offline_hook.py')] if store else [],
    excludes=['PyQt5', 'PyQt6', 'PySide2', 'tkinter'] + (PYTHON_EXCLUDES + remote if store else []),
    noarchive=False,
    # Only LGPL bindings are external sources; own application modules remain in PYZ.
    module_collection_mode={'PySide6': 'py', 'shiboken6': 'py'} if standalone else {},
)
if store:
    omit_system_copies(a, json.loads((root / 'distribution/windows/signing/retired-system-copies.json').read_text()))
    record_analysis(a, root / 'evidence/qt-minimal/build-inputs.json')
if store and any(name == module or name.startswith(module + '.')
                 for name, _, _ in a.pure for module in remote):
    raise RuntimeError('Remote module leaked into offline Store payload')
pyz = PYZ(a.pure)
exe = EXE(
    pyz, a.scripts, [], exclude_binaries=True, name=name,
    debug=False, strip=False, upx=False, console=False,
    icon=str(prepared / 'AgroLines.ico'), version=str(prepared / 'version.txt'),
)
coll = COLLECT(exe, a.binaries, a.datas, strip=False, upx=False, name=name)
