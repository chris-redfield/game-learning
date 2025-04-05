# -*- mode: python ; coding: utf-8 -*-
import os
import platform

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('assets', 'assets'),  # Include the assets folder
        ('entities', 'entities'),  # Include the entities folder and its contents
        ('items', 'items'),  # Include the items folder and its contents
    ],
    hiddenimports=[
        # Enemy modules
        'entities.enemy',
        'entities.enemy.enemy',
        'entities.enemy.enemy_attribute',
        'entities.enemy.skeleton',
        'entities.enemy.slime',
        
        # Other entities
        'entities.grass',
        'entities.soul',
        'entities.blood_particle',
        'entities.bonfire',
        'entities.rock',
        
        # Player modules
        'entities.player.player',
        'entities.player.attributes',
        'entities.player.particles',
        'entities.player.skill_tree',
        'entities.player.sprite_sheet',
        
        # Items
        'items',
        'items.item',
        'items.ancient_scroll',
        'items.dragon_heart',
        'items.health_potion',
        
        # Game modules
        'character_screen',
        'constants',
        'death_screen',
        'hud',
        'inventory',
        'map',
        'world'
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
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='The Dark Garden of Z',  # Updated to match build.py
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Set to True if you want to see console output for debugging
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    # Platform-specific icon handling (skip on Linux)
icon=(
    'assets/icon.ico' if platform.system() == 'Windows' and os.path.exists('assets/icon.ico')
    else 'assets/icon.icns' if platform.system() == 'Darwin' and os.path.exists('assets/icon.icns')
    else None  # Skip icon on Linux as PyInstaller doesn't support it
),
)