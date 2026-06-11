# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_data_files, collect_dynamic_libs

block_cipher = None

ctk_data = collect_data_files('customtkinter')
sr_data  = collect_data_files('speech_recognition')

a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=collect_dynamic_libs('sounddevice'),
    datas=ctk_data + sr_data,
    hiddenimports=[
        'customtkinter',
        'PIL._tkinter_finder',
        'anthropic',
        'sounddevice',
        'speech_recognition',
        'numpy',
        'sqlite3',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='Gestao Efcaz',
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
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Gestao Efcaz',
)
