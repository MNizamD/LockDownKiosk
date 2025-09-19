# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

# --- Analysis for LockDown ---
a1 = Analysis(
    ['LockDown.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)

pyz1 = PYZ(a1.pure)

exe1 = EXE(
    pyz1,
    a1.scripts,
    [],
    exclude_binaries=True,
    name='LockDown',
    debug=False,
    bootloader_ignore_signals=False,
    strip=True,
    upx=True,
    console=True,
)

# --- Analysis for Main ---
a2 = Analysis(
    ['Main.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)

pyz2 = PYZ(a2.pure)

exe2 = EXE(
    pyz2,
    a2.scripts,
    [],
    exclude_binaries=True,
    name='Main',
    debug=False,
    bootloader_ignore_signals=False,
    strip=True,
    upx=True,
    console=False,
)

# --- Analysis for Updater (one-file build) ---
a3  = Analysis(
    ['Updater.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz3 = PYZ(a3.pure)

exe3 = EXE(
    pyz3,
    a3.scripts,
    a3.binaries,
    a3.datas,
    [],
    name='Updater',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

# --- Collect LockDown + Main into one dist folder ---
coll = COLLECT(
    exe1,
    exe2,
    a1.binaries + a2.binaries,
    a1.datas + a2.datas,
    strip=True,
    upx=True,
    name='NizamLab',
)

# --- Extra: move standalone Updater.exe into NizamLab ---
import shutil, os
distpath = os.path.join(os.getcwd(), 'dist')
src = os.path.join(distpath, 'Updater.exe')
dst = os.path.join(distpath, 'NizamLab', 'Updater.exe')

if os.path.exists(src):
    shutil.move(src, dst)