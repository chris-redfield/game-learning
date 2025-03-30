#!/usr/bin/env python3
"""
Build script for creating game executables for multiple platforms.
Run this script to build the game for your current platform.
"""

import os
import sys
import platform
import subprocess
import shutil

# Game details
GAME_NAME = "DynamicWorldGame"
VERSION = "1.0.0"
MAIN_SCRIPT = "main.py"

# Determine the current platform
current_platform = platform.system().lower()

def clean_build_dirs():
    """Clean up build directories"""
    for dir_name in ['build', 'dist']:
        if os.path.exists(dir_name):
            print(f"Cleaning {dir_name} directory...")
            shutil.rmtree(dir_name)

def create_windows_build():
    """Create a Windows executable"""
    print("Building for Windows...")
    
    # Check if icon exists, if not create a placeholder message
    icon_path = "assets/icon.ico"
    icon_param = f"--icon={icon_path}" if os.path.exists(icon_path) else ""
    
    # Data files - use Windows path separator
    data_params = [
        "--add-data", "assets;assets",
        "--add-data", "entities;entities"
    ]
    
    # Hidden imports to ensure all modules are included
    hidden_imports = [
        "--hidden-import", "entities.enemy",
        "--hidden-import", "entities.skeleton",
        "--hidden-import", "entities.slime", 
        "--hidden-import", "entities.grass",
        "--hidden-import", "entities.soul",
        "--hidden-import", "entities.player.player",
        "--hidden-import", "entities.player.attributes",
        "--hidden-import", "entities.player.particles"
    ]
    
    cmd = [
        "pyinstaller",
        "--name", GAME_NAME,
        "--onefile",
        "--windowed",
    ] + data_params + hidden_imports
    
    # Add icon if exists
    if icon_param:
        cmd.append(icon_param)
        
    # Add main script last
    cmd.append(MAIN_SCRIPT)
    
    # Remove empty strings
    cmd = [item for item in cmd if item]
    
    # Print the command for debugging
    print("Running command:", " ".join(cmd))
    
    # Run the command
    subprocess.run(cmd, check=True)

def create_macos_build():
    """Create a macOS application bundle"""
    print("Building for macOS...")
    
    # Check if icon exists
    icon_path = "assets/icon.icns"
    icon_param = f"--icon={icon_path}" if os.path.exists(icon_path) else ""
    
    # Data files - use macOS path separator
    data_params = [
        "--add-data", "assets:assets",
        "--add-data", "entities:entities"
    ]
    
    # Hidden imports to ensure all modules are included
    hidden_imports = [
        "--hidden-import", "entities.enemy",
        "--hidden-import", "entities.skeleton",
        "--hidden-import", "entities.slime", 
        "--hidden-import", "entities.grass",
        "--hidden-import", "entities.soul",
        "--hidden-import", "entities.player.player",
        "--hidden-import", "entities.player.attributes",
        "--hidden-import", "entities.player.particles"
    ]
    
    cmd = [
        "pyinstaller",
        "--name", GAME_NAME,
        "--windowed",
    ] + data_params + hidden_imports
    
    # Add icon if exists
    if icon_param:
        cmd.append(icon_param)
    
    # Add bundle identifier for macOS
    cmd.extend(["--osx-bundle-identifier", f"com.yourgame.{GAME_NAME.lower()}"])
    
    # Add main script last
    cmd.append(MAIN_SCRIPT)
    
    # Remove empty strings
    cmd = [item for item in cmd if item]
    
    # Print the command for debugging
    print("Running command:", " ".join(cmd))
    
    # Run the command
    subprocess.run(cmd, check=True)

def create_linux_build():
    """Create a Linux executable"""
    print("Building for Linux...")
    
    # Data files - use Linux path separator
    data_params = [
        "--add-data", "assets:assets",
        "--add-data", "entities:entities"
    ]
    
    # Hidden imports to ensure all modules are included
    hidden_imports = [
        "--hidden-import", "entities.enemy",
        "--hidden-import", "entities.skeleton",
        "--hidden-import", "entities.slime", 
        "--hidden-import", "entities.grass",
        "--hidden-import", "entities.soul",
        "--hidden-import", "entities.player.player",
        "--hidden-import", "entities.player.attributes",
        "--hidden-import", "entities.player.particles"
    ]
    
    cmd = [
        "pyinstaller",
        "--name", GAME_NAME,
        "--onefile",
        "--windowed",
    ] + data_params + hidden_imports
    
    # Add main script last
    cmd.append(MAIN_SCRIPT)
    
    # Print the command for debugging
    print("Running command:", " ".join(cmd))
    
    # Run the command
    subprocess.run(cmd, check=True)

def main():
    """Main build function"""
    # Clean up previous builds
    clean_build_dirs()
    
    # Build for the current platform
    if current_platform == "windows":
        create_windows_build()
    elif current_platform == "darwin":  # macOS
        create_macos_build()
    elif current_platform == "linux":
        create_linux_build()
    else:
        print(f"Unsupported platform: {current_platform}")
        return 1
    
    print(f"\nBuild completed for {current_platform}!")
    print(f"Your executable can be found in the 'dist' directory.")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())