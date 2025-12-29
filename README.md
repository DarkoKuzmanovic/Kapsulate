# Kapsulate 💊

**Kapsulate** is a powerful system enhancement tool for Linux (KDE Plasma 6 / Wayland) that supercharges your Caps Lock key.

It is a port of the [original Windows/AutoHotkey version](https://github.com/DarkoKuzmanovic/Capsulate), adapted for the modern Linux security model using `keyd` and Python.

## ✨ Features

- **Smart Caps Lock**: Acts as `Esc` when tapped, and a `Hyper` modifier when held.
- **Vim-style Navigation**: H/J/K/L for arrow keys (and more).
- **Text Transformation**: Convert text to CamelCase, UPPERCASE, etc., on the fly.
- **System Integration**: Quick access to Task Manager, Volume, and Windows.

## 🔧 Installation

### 1. Requirements

- Python 3.12+
- `keyd` (Input remapping daemon)
- `wl-clipboard` (Wayland clipboard utilities)

### 2. Setup

```bash
# Clone the repo
git clone https://github.com/DarkoKuzmanovic/Kapsulate-Linux.git
cd Kapsulate-Linux

# Install Python dependencies
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Install keyd config (Requires sudo)
sudo cp config/kapsulate.conf /etc/keyd/kapsulate.conf
sudo systemctl restart keyd
```

## 🚀 Usage

Run the GUI daemon:
```bash
python src/main.py
```
