# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['lxgrtgr_annotate_gui_77.py'],
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
a.datas += Tree('./en_core_web_trf', prefix = 'en_core_web_trf')
a.datas += Tree('./en_core_web_trf-3.5.0.dist-info', prefix = 'en_core_web_trf-3.5.0.dist-info')

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='lxgrtgr_annotate_gui_77',
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
