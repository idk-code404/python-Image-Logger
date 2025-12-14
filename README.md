# 🤖 Auto Image Logger

A professional, automated screenshot logger with Discord integration and IP geolocation capabilities. Capture screenshots automatically and receive them with location data in your Discord channel.

## 📋 Features

- **🖥️ Automatic Screenshot Capture**: Periodic screenshots without user intervention
- **🌍 IP Geolocation**: Approximate location based on public IP address
- **📨 Discord Integration**: Send screenshots directly to Discord webhooks
- **⚙️ Configurable**: Adjustable intervals, quality, and capture limits
- **📊 System Monitoring**: Optional CPU, memory, and disk usage tracking
- **🔄 Background Operation**: Runs silently without user interaction
- **📁 Local Storage**: Optionally save screenshots locally
- **🔒 Privacy-Focused**: No external servers, direct Discord communication

## ⚠️ Important Disclaimer

**USE RESPONSIBLY AND ETHICALLY!**

- This tool is intended **only for monitoring devices you own or have explicit permission to monitor**
- Using this on others' devices without consent may be **illegal** and **unethical**
- Check local privacy laws before deployment
- For legal use cases only (personal monitoring, parental controls with disclosure, authorized employee monitoring)

## 🚀 Quick Start

### Prerequisites
- Windows 10/11 or Linux/Mac
- Python 3.8+ (for development/build)
- Discord account and server (for webhook)

### Installation Options

#### **Option A: Quick Install (Executable)**
1. Download the latest release from [Releases](#)
2. Extract the ZIP file
3. Edit `auto_config.json` with your Discord webhook URL
4. Run `start_logger.bat` (Windows) or `start_logger.sh` (Linux/Mac)

#### **Option B: Python Installation**
```bash
# 1. Clone or download the repository
git clone https://github.com/yourusername/auto-image-logger.git
cd auto-image-logger

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure your webhook
# Edit auto_config.json with your Discord webhook URL

# 4. Run the logger
python auto_image_logger.py
```

#### **Option C: Build from Source**
```bash
# 1. Install dependencies
pip install pyinstaller requests pillow psutil

# 2. Build executable
python build_exe.py

# 3. Find your .exe in the 'dist' folder
```

## ⚙️ Configuration

Edit `auto_config.json`:

```json
{
  "webhook_url": "YOUR_DISCORD_WEBHOOK_URL_HERE",
  "capture_interval": 300,
  "image_quality": 85,
  "max_captures": 0,
  "save_locally": true,
  "local_save_path": "auto_captures",
  "capture_location": true,
  "log_level": "INFO"
}
```

### Key Settings

| Setting | Default | Description |
|---------|---------|-------------|
| `webhook_url` | Required | Your Discord webhook URL |
| `capture_interval` | 300 | Seconds between captures (5 min) |
| `image_quality` | 85 | JPEG quality (1-100) |
| `max_captures` | 0 | Maximum captures (0 = unlimited) |
| `save_locally` | true | Save screenshots locally |
| `capture_location` | true | Enable IP geolocation |
| `start_delay` | 10 | Seconds before first capture |
| `log_level` | INFO | Logging verbosity |

## 🎯 Usage

### Starting the Logger
```bash
# Python version
python auto_image_logger.py

# Executable version (Windows)
AutoImageLogger.exe

# With launcher script (Windows)
start_logger.bat
```

### Discord Webhook Setup
1. Go to your Discord server settings
2. Navigate to **Integrations → Webhooks**
3. Click **New Webhook**
4. Configure and copy the webhook URL
5. Paste it into `auto_config.json`

### Stopping the Logger
- **Windows**: Close the console window or use Task Manager
- **Linux/Mac**: `Ctrl+C` in terminal or `kill [PID]`
- **Background**: Use system service controls

## 📁 Project Structure
```
auto-image-logger/
├── auto_image_logger.py      # Main Python script
├── auto_config.json          # Configuration file
├── build_exe.py             # EXE builder script
├── requirements.txt          # Python dependencies
├── dist/                    # Built executables
│   ├── AutoImageLogger.exe  # Windows executable
│   ├── start_logger.bat     # Windows launcher
│   └── auto_config.json     # Configuration
├── auto_captures/           # Locally saved screenshots
├── session_logs/            # Session information
└── logs/                    # Log files
```

## 🛠️ Building the Executable

### Requirements
- Python 3.8+
- PyInstaller (`pip install pyinstaller`)

### Build Commands
```bash
# Automatic build (recommended)
python build_exe.py

# Manual build (Windows)
pyinstaller --onefile --windowed --clean --name AutoImageLogger --add-data "auto_config.json;." auto_image_logger.py

# Manual build (Linux/Mac)
pyinstaller --onefile --windowed --clean --name AutoImageLogger --add-data "auto_config.json:." auto_image_logger.py
```

### Custom Icon
1. Convert your image to `.ico` format (256x256 recommended)
2. Save as `icon.ico` in the project root
3. Rebuild the executable

## 🔧 Advanced Configuration

### Location Services
The logger supports multiple geolocation APIs:
- `ipapi` (default) - Free, 45 requests/minute limit
- `ipapi_co` - Alternative service
- `geolocation` - Simple endpoint

### System Integration

#### **Windows: Run at Startup**
1. Create shortcut to `AutoImageLogger.exe`
2. Press `Win + R`, type `shell:startup`
3. Paste shortcut in Startup folder

#### **Linux: Systemd Service**
```bash
# Copy service file
sudo cp auto-image-logger.service /etc/systemd/system/

# Enable and start
sudo systemctl daemon-reload
sudo systemctl enable auto-image-logger
sudo systemctl start auto-image-logger

# Check status
sudo systemctl status auto-image-logger
```

## 🐛 Troubleshooting

### Common Issues

| Problem | Solution |
|---------|----------|
| "Webhook URL not configured" | Edit `auto_config.json` with your webhook |
| "Failed to send to Discord" | Check internet connection and webhook URL |
| "Cannot write mode RGBA as JPEG" | Update PIL/Pillow: `pip install --upgrade pillow` |
| "Location service timeout" | Increase `location_timeout` in config |
| Anti-virus flags .exe | Add exception or build from source |
| Large file size | Use UPX compression in build_exe.py |

### Logs and Debugging
- Check `auto_logger.log` for detailed logs
- Enable debug mode: Set `"log_level": "DEBUG"` in config
- Monitor `session_logs/` for session information

### Discord Rate Limits
- Discord webhooks have rate limits
- Default 5-minute interval avoids hitting limits
- If you increase frequency, monitor for 429 errors

## 📊 Sample Discord Output

The logger sends rich embeds to Discord containing:
- Screenshot image
- System information (OS, Python version, etc.)
- Approximate location (city, country, coordinates)
- ISP information
- Google Maps link
- Session and capture numbers

## 🔒 Privacy & Security

### What Data is Collected
- Screenshots of the display
- Public IP address (for geolocation)
- Basic system information
- Network ISP information

### What is NOT Collected
- Keystrokes or passwords
- Microphone/camera access
- Personal files or documents
- Browser history
- Application-specific data

### Data Storage
- Screenshots: Only sent to your Discord, optionally saved locally
- Logs: Local files only, not transmitted
- Configuration: Local JSON file, not shared

## ⚖️ Legal Compliance

### GDPR Considerations
If used in EU countries:
- Inform users about monitoring
- Obtain explicit consent
- Provide data access and deletion options
- Limit data retention

### Corporate Use
For employee monitoring:
- Clear policies about monitoring
- Written consent from employees
- Legal review before deployment
- Limited to work hours/devices

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

### Development Setup
```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Linux/Mac)
source venv/bin/activate

# Install development dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt  # If available
```

## 📄 License

This project is provided for educational and authorized monitoring purposes only. Users are responsible for complying with all applicable laws and regulations.

## 📞 Support

For issues and questions:
1. Check the [Troubleshooting](#-troubleshooting) section
2. Review open/closed issues on GitHub
3. Create a new issue with details and logs

## 🚨 Emergency Stop

If you need to immediately stop the logger:

### **Windows**
1. Open Task Manager (`Ctrl+Shift+Esc`)
2. Find `AutoImageLogger.exe` or `python.exe`
3. Click "End Task"

### **Linux/Mac**
```bash
# Find and kill the process
ps aux | grep auto_image_logger
kill [PID]

# Or kill all instances
pkill -f auto_image_logger
```

---

**⚠️ Remember**: With great power comes great responsibility. Use this tool ethically and legally.

---
