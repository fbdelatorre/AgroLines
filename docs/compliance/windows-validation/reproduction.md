# Isolated Windows LGPL laboratory — 0BSD synthetic code only

Requires an x64 MSVC developer shell, Git, CMake 4.4.4, Ninja 1.13.2, Python 3.12.10
and PyInstaller 6.22.3 on a **build/lab host**, not an end-user installation.
Use trusted official tools already available; do not change any code integrity policy
if a tool/consumer is blocked. No MSIX installation, certificates, signing or Store access.

From repository root, in an MSVC x64 developer environment:

```
python -m pytest -q tools/windows-lgpl-lab/test_lab.py
python tools/windows-lgpl-lab/run.py --component qtbase-6.12.0 --work C:/lab/qt-fresh
python tools/windows-lgpl-lab/run.py --component geos-3.11.3 --work C:/lab/geos311-fresh
python tools/windows-lgpl-lab/run.py --component geos-3.14.1 --work C:/lab/geos314-fresh
```

Each work directory must be new. Sources are pinned to official commits and their
committed Git archive digest in the existing source index, with explicit LF/archive
umask to avoid host Git conversion. TLS/hash verification is never disabled.
Qt Core is compiled with GUI/network and the unrelated windeployqt tool disabled;
these are lab-only flags, not a proposed production feature change.

Original source → build → original consumer run → harmless version-string-only
patch → rebuild library → same consumer with modified library. Qt uses QString and
qVersion, GetModuleFileNameW records actual loaded module. Both GEOS versions use
C API polygon areas at four scales, actual HMODULE path and self module enumeration.
GEOS repeats the operations with the **same frozen synthetic PyInstaller executable**.
The caller checks paths, marker phase, x64 PE machine, changed DLL hashes, unchanged
areas, frozen mode and dependencies confined to the selected lab directory.

The frozen synthetic GEOS executable takes an external library argument. It does
not include Shapely/Fiona or AgroLines; it proves this limited freezer mechanism,
not replacement through their wheel import repairs or the proprietary application.
No proprietary material is included in consumer, patch or output artifacts.
Existing 22 computational references run separately against the baseline GIS engine;
they are not relabeled as 22 tests of the compiled lab library. Lab area checks are
additional and deliberately distinct.

Results/patch/CMakeCache are uploaded by windows-lgpl-lab.yml; binaries/sources and
application bytecode are not uploaded. Windows build host security state is recorded
without modification and never treated as Windows 11 physical SAC acceptance.
Read [the scoped analysis](README.md) before
interpreting the results. The 0BSD license applies only to synthetic consumer/lab code; generated Qt/GEOS
patches retain the original applicable LGPL terms and copyrights. The read-only
evidence capture workflow supplements original headers and full LGPL/GPL texts.
This does not change the AgroLines license.
