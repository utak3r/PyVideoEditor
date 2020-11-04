# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

added_files = [
    ( 'app.ico', '.' ),
	( 'PyVideoEditor/PyVideoEditorMainWindow.ui', 'PyVideoEditor' ),
    ( 'PyVideoEditor/Settings.ui', 'PyVideoEditor' ),
    ( 'PyVideoEditor/ProcessRunner.ui', 'PyVideoEditor' )
]

a = Analysis(['PyVideoEditor/__main__.py'],
             pathex=['D:\\devel\\sandbox\\PyVideoEditor'],
             binaries=[],
             datas=added_files,
             hiddenimports=['PySide2.QtXml'],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='PyVideoEditor',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=False,
          icon='app.ico')
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='PyVideoEditor')
