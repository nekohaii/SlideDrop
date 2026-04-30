# -*- mode: python ; coding: utf-8 -*-

from pathlib import Path

from PyInstaller.utils.hooks import collect_data_files, collect_dynamic_libs, collect_submodules


project_root = Path(SPECPATH).parent
entrypoint = project_root / "run.py"
icon_path = project_root / "assets" / "slidedrop.icns"

datas = []
datas += collect_data_files("customtkinter")
datas += collect_data_files("tkinterdnd2")

binaries = []
binaries += collect_dynamic_libs("tkinterdnd2")

hiddenimports = []
hiddenimports += collect_submodules("customtkinter")
hiddenimports += collect_submodules("tkinterdnd2")


a = Analysis(
    [str(entrypoint)],
    pathex=[str(project_root), str(project_root / "src")],
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
    [],
    exclude_binaries=True,
    name="SlideDrop",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=str(icon_path) if icon_path.exists() else None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="SlideDrop",
)

app = BUNDLE(
    coll,
    name="SlideDrop.app",
    icon=str(icon_path) if icon_path.exists() else None,
    bundle_identifier="com.slidedrop.app",
    info_plist={
        "CFBundleName": "SlideDrop",
        "CFBundleDisplayName": "SlideDrop",
        "CFBundleShortVersionString": "0.1.0",
        "CFBundleVersion": "0.1.0",
        "NSHighResolutionCapable": True,
    },
)
