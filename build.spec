# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['main.py'],
    datas=[('assets', 'assets')],
    hiddenimports=['PIL._tkinter_finder'],
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    name='주인님_확인해주세요',
    console=False,
    onefile=True,
)
