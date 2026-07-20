# -*- mode: python ; coding: utf-8 -*-

import runpy
from pathlib import Path

__version__ = runpy.run_path("log_cleaner/version.py")["__version__"]
version_parts = tuple(int(part) for part in __version__.split("."))
file_version = version_parts + (0,) * (4 - len(version_parts))
version_info_path = Path("build") / "version_info.txt"
version_info_path.parent.mkdir(exist_ok=True)
version_info_path.write_text(
    f"""VSVersionInfo(
  ffi=FixedFileInfo(
    filevers={file_version},
    prodvers={file_version},
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
  ),
  kids=[
    StringFileInfo([
      StringTable(
        '040904B0',
        [
          StringStruct('CompanyName', 'jmveigac'),
          StringStruct('FileDescription', 'Log Cleaner'),
          StringStruct('FileVersion', '{__version__}'),
          StringStruct('InternalName', 'log-cleaner'),
          StringStruct('OriginalFilename', 'log-cleaner.exe'),
          StringStruct('ProductName', 'Log Cleaner'),
          StringStruct('ProductVersion', '{__version__}')
        ]
      )
    ]),
    VarFileInfo([VarStruct('Translation', [1033, 1200])])
  ]
)
""",
    encoding="utf-8",
)

a = Analysis(
    ["main.py"],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="log-cleaner",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    version=str(version_info_path),
)
