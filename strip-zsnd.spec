# type: ignore
from PyInstaller.utils.hooks import collect_all
from pathlib import Path
import os

datas, binaries, hiddenimports = collect_all("rich._unicode_data")

# Include documents for the "rich" package
for p in Path(os.getcwd()).resolve().rglob("**/site-packages/rich-*"):
    datas.append((str(p / 'LICENSE'), p.name))
    datas.append((str(p / 'METADATA'), p.name))

a = Analysis(
    ["strip-zsnd.py"],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    exclude_binaries=True,
    name="strip-zsnd",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    # upx_exclude=[],
    # runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name="strip-zsnd",
)
