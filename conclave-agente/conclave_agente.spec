# -*- mode: python ; coding: utf-8 -*-
# CÓNCLAVE Agente — PyInstaller Build Spec
# © 2026 ceob68 / Vaultly. All rights reserved.
#
# Build command (from project root with venv active):
#   pyinstaller conclave_agente.spec
#
# Output: dist/CONCLAVE_Agente/CONCLAVE_Agente.exe

import sys
from pathlib import Path

block_cipher = None

# Collect all backend and gui modules
added_files = [
    ('config',        'config'),
    ('README.txt',    '.'),
    ('LICENSE.txt',   '.'),
]

a = Analysis(
    ['desktop_app.py'],
    pathex=['.'],
    binaries=[],
    datas=added_files,
    hiddenimports=[
        'PySide6.QtCore',
        'PySide6.QtGui',
        'PySide6.QtWidgets',
        'backend',
        'backend.ai_engine',
        'backend.orchestrator',
        'backend.database',
        'gui',
        'gui.main_window',
        'gui.ai_worker',
        'gui.components',
        'gui.app_style',
        'gui.customization_dialog',
        'gui.diagnosis_dialog',
        'sqlite3',
        'json',
        'threading',
        'gc',
        # Transformers / torch lazy imports
        'transformers',
        'accelerate',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'notebook',
        'ipython',
        'pytest',
        'tkinter',
    ],
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
    name='CONCLAVE_Agente',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,          # No console window for end user
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    # icon='assets/icon.ico',  # Uncomment after adding icon
    version_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='CONCLAVE_Agente',
)
