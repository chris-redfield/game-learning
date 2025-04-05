#!/usr/bin/env python3
"""
Build script for creating game executables for multiple platforms.
Run this script to build the game for your current platform.
Uses the game.spec file for build configuration.
"""

import os
import sys
import platform
import subprocess
import shutil
from pathlib import Path

# Determine the current platform
current_platform = platform.system().lower()

def clean_build_dirs():
    """Clean up build directories"""
    for dir_name in ['build', 'dist']:
        if os.path.exists(dir_name):
            print(f"Cleaning {dir_name} directory...")
            shutil.rmtree(dir_name)

def create_windows_build():
    """Create a Windows executable using the .spec file"""
    print("Building for Windows...")
    cmd = ["pyinstaller", "game.spec"]
    
    # Print the command for debugging
    print("Running command:", " ".join(cmd))
    
    # Run the command
    subprocess.run(cmd, check=True)

def create_macos_build():
    """Create a macOS application bundle using the .spec file"""
    print("Building for macOS...")
    cmd = ["pyinstaller", "game.spec"]
    
    # Print the command for debugging
    print("Running command:", " ".join(cmd))
    
    # Run the command
    subprocess.run(cmd, check=True)

def create_linux_build():
    """Create a Linux executable using the .spec file"""
    print("Building for Linux...")
    cmd = ["pyinstaller", "game.spec"]
    
    # Print the command for debugging
    print("Running command:", " ".join(cmd))
    
    # Run the command
    result = subprocess.run(cmd, check=True)
    
    # If build was successful, do Linux-specific steps
    if result.returncode == 0:
        print("Performing Linux-specific post-build steps...")
        linux_post_build()
        
def linux_post_build():
    """Perform Linux-specific post-build steps"""
    # 1. Rename the executable to The_Dark_Garden_of_Z
    dist_dir = Path("dist")
    if not dist_dir.exists():
        print("Error: dist directory not found!")
        return
        
    # Find the executable - could be named with spaces or with the .spec's name
    found = False
    for file in dist_dir.iterdir():
        if file.is_file() and os.access(file, os.X_OK):
            # This is likely our executable
            target_name = dist_dir / "The_Dark_Garden_of_Z"
            if file.name != "The_Dark_Garden_of_Z":
                print(f"Renaming executable: {file.name} -> The_Dark_Garden_of_Z")
                # Rename the file
                shutil.move(str(file), str(target_name))
                found = True
            else:
                found = True
            break
    
    if not found:
        print("Warning: Could not find executable to rename!")
        return
        
    # 2. Copy the existing .desktop file to applications directory
    desktop_file_path = "The_Dark_Garden_of_Z.desktop"
    if not os.path.exists(desktop_file_path):
        print(f"Error: {desktop_file_path} not found!")
        return
        
    applications_dir = os.path.expanduser("~/.local/share/applications")
    if not os.path.exists(applications_dir):
        os.makedirs(applications_dir, exist_ok=True)
        
    target_path = os.path.join(applications_dir, desktop_file_path)
    print(f"Copying .desktop file to: {target_path}")
    shutil.copy2(desktop_file_path, target_path)
    
    print("✅ Linux post-build steps completed successfully!")
    print(f"✨ Your application should now appear in your applications menu")
    print(f"🚀 You can also run it directly from: {dist_dir}/The_Dark_Garden_of_Z")

def main():
    """Main build function"""
    # Check if game.spec exists
    if not os.path.exists("game.spec"):
        print("Error: game.spec file not found!")
        print("Please ensure the game.spec file exists in the current directory.")
        return 1
        
    # Clean up previous builds
    clean_build_dirs()
    
    # Build for the current platform
    try:
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
        
        if current_platform == "linux":
            print(f"Your executable can be found at 'dist/The_Dark_Garden_of_Z' and should appear in your applications menu.")
        else:
            print(f"Your executable can be found in the 'dist' directory.")
        
        return 0
    except Exception as e:
        print(f"Error during build: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())