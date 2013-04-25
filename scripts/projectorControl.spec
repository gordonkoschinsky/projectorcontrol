# -*- mode: python -*-
a = Analysis(['C:\\Users\\gordon\\Documents\\Coding\\projectorControl\\src\\projectorControl\\projectorControl.py'],
             pathex=['C:\\Users\\gordon\\Documents\\Coding\\projectorControl',
                     'C:\\Users\\gordon\\Documents\\Coding\\projectorControl\\Lib\\site-packages',
                     'C:\\Users\\gordon\\Documents\\Coding\\pyinstaller-2.0'],
             hiddenimports=[],
             hookspath=None)
pyz = PYZ(a.pure)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name=os.path.join('dist', 'projectorControl.exe'),
          debug=False,
          strip=None,
          upx=True,
          console=False,
          icon="C:\\Users\\gordon\\Documents\\Coding\\projectorControl\\src\\res\\video_projector.ico"
        )
