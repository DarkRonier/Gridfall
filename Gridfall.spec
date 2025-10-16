# -*- mode: python ; coding: utf-8 -*-
import glob

block_cipher = None

# Recopilar archivos de assets
datas = []

print("\n" + "="*60)
print("VERIFICANDO ARCHIVOS EN assets/:")
print("="*60)

# SVGs de piezas en assets/pieces/
archivos_piezas = glob.glob('assets/pieces/*.svg')
print(f"SVGs de piezas encontrados: {len(archivos_piezas)}")
for svg in archivos_piezas:
    print(f"  ✓ {svg}")
    datas.append((svg, 'assets/pieces'))

# Iconos en assets/icons/
archivos_icons = glob.glob('assets/icons/*.svg')
print(f"\nIconos encontrados: {len(archivos_icons)}")
for svg in archivos_icons:
    print(f"  ✓ {svg}")
    datas.append((svg, 'assets/icons'))

# Sonidos en assets/sounds/
archivos_sounds = glob.glob('assets/sounds/*')
print(f"\nSonidos encontrados: {len(archivos_sounds)}")
for sound in archivos_sounds:
    print(f"  ✓ {sound}")
    datas.append((sound, 'assets/sounds'))

print(f"\nTOTAL DE ARCHIVOS A EMPAQUETAR: {len(datas)}")
print("="*60 + "\n")

if len(datas) == 0:
    print("⚠️  ADVERTENCIA: No se encontraron archivos para empaquetar!")

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=[],
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
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='Gridfall',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)