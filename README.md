# Kapsulate 💊

**Kapsulate** is a powerful system enhancement tool for Linux (KDE Plasma 6 / Wayland) that supercharges your Caps Lock key.

It is a port of the [original Windows/AutoHotkey version](https://github.com/DarkoKuzmanovic/Capsulate), adapted for the modern Linux security model using `keyd` and Python.

## ✨ Features

- **Smart Caps Lock**: Acts as `Esc` when tapped, and a `Hyper` modifier when held
- **Vim-style Navigation**: H/J/K/L for arrow keys (and more)
- **Text Transformation**: Convert text to CamelCase, UPPERCASE, etc., on the fly
- **System Integration**: Quick access to Task Manager, Volume, and Windows
- **System Tray**: Intuitive tray icon with context menu
- **Theme Aware**: Automatically adapts to dark/light theme changes
- **Autostart Support**: Option to start with system (DEB package only)
- **Error Notifications**: Tray notifications for important events

## 🔧 Installation

### Option 1: DEB Package (Recommended)

Download the latest `.deb` package from the [Releases page](https://github.com/DarkoKuzmanovic/Kapsulate/releases) and install:

```bash
sudo dpkg -i kapsulate_*.deb
sudo apt-get install -f  # If dependencies are missing
```

After installation, you can launch Kapsulate from your application menu or by running:

```bash
kapsulate
```

### Option 2: Development Mode

#### 1. Requirements

- Python 3.12+
- `keyd` (Input remapping daemon)
- `python3-pyqt6` (Qt6 Python bindings)
- `python3-dbus` (DBus Python bindings)

#### 2. Setup

```bash
# Clone the repository
git clone https://github.com/DarkoKuzmanovic/Kapsulate.git
cd Kapsulate

# Install Python dependencies
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Install keyd config (requires sudo)
sudo cp config/kapsulate.conf /etc/keyd/kapsulate.conf
sudo systemctl restart keyd
```

## 🚀 Usage

### Running the Application

**DEB Package:**

```bash
kapsulate
```

**Development Mode:**

```bash
python src/main.py
```

Or use the CLI interface:

```bash
python src/cli.py
```

### System Tray Menu

Right-click the tray icon to access:

- **Open Config** - Opens the keyd configuration file
- **Reload Config** - Restarts the keyd service to apply changes
- **Start with system** - Enable/disable autostart (DEB package only)
- **About Kapsulate** - View version and author information
- **Quit** - Exit the application

### Autostart (DEB Package Only)

When installed via DEB package, you can enable autostart:

1. Run Kapsulate
2. Right-click the tray icon
3. Toggle "Start with system"

This creates a symlink at `~/.config/autostart/kapsulate.desktop` that will be automatically launched on login.

## 📁 File Locations

| Location                                      | Purpose                                |
| --------------------------------------------- | -------------------------------------- |
| `/usr/bin/kapsulate`                          | Main executable (DEB package)          |
| `/usr/share/kapsulate/`                       | Python source code (DEB package)       |
| `/etc/kapsulate/kapsulate.conf`               | Default configuration (DEB package)    |
| `~/.config/kapsulate/kapsulate.conf`          | User-specific configuration (optional) |
| `~/.local/share/kapsulate/logs/kapsulate.log` | Application logs                       |
| `~/.config/autostart/kapsulate.desktop`       | Autostart symlink (user-enabled)       |

## 🔍 Troubleshooting

### Application won't start

**PermissionError related to logs:**
Ensure you have the latest version. Logs are now stored in `~/.local/share/kapsulate/logs/kapsulate.log`.

**Missing dependencies:**

```bash
sudo apt-get install python3-pyqt6 python3-dbus keyd
```

### Autostart not working

Check if the symlink exists:

```bash
ls -la ~/.config/autostart/kapsulate.desktop
```

Check if the desktop file is installed:

```bash
ls -la /usr/share/applications/kapsulate.desktop
```

### View logs

```bash
cat ~/.local/share/kapsulate/logs/kapsulate.log
```

## 📦 Building from Source

To build a DEB package locally:

```bash
chmod +x build_deb.sh
./build_deb.sh
```

This creates `build/kapsulate_1.0.0_amd64.deb`.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Original [Capsulate](https://github.com/DarkoKuzmanovic/Capsulate) for Windows/AutoHotkey
- [keyd](https://github.com/rvaiya/keyd) for the keyboard remapping daemon
- The KDE Plasma community for the excellent desktop environment

## 📞 Support

- 🐛 [Report a bug](https://github.com/DarkoKuzmanovic/Kapsulate/issues)
- 💡 [Request a feature](https://github.com/DarkoKuzmanovic/Kapsulate/issues)
- 📖 [Documentation](https://github.com/DarkoKuzmanovic/Kapsulate/wiki)
