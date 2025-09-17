# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

# --- Analysis for LockDown (Launcher) ---
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
    strip=True,          # strip for smaller + faster load
    upx=True,
    console=False,
)

# --- Analysis for Main (Start) ---
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

# --- Collect into one dist folder ---
coll = COLLECT(
    exe1,
    exe2,
    a1.binaries + a2.binaries,
    a1.datas + a2.datas,
    strip=True,
    upx=True,
    name='NizamLab',  # final dist folder
)
