# Kapsulate DEB Packaging Guide

This guide explains how to build and install Kapsulate as a `.deb` package.

## Automated Releases

Kapsulate uses GitHub Actions to automatically build and publish DEB packages when you push a new version tag.

### Creating a Release

1. Update the version in [`packaging/DEBIAN/control`](packaging/DEBIAN/control:2) and [`CHANGELOG.md`](CHANGELOG.md:1)
2. Commit your changes
3. Create and push a version tag:

```bash
git tag v1.0.1
git push origin v1.0.1
```

4. GitHub Actions will automatically:

   - Build the DEB package
   - Create a GitHub Release
   - Upload the `.deb` file and SHA256 checksums

5. Users can download and install from the [Releases page](https://github.com/DarkoKuzmanovic/Kapsulate/releases)

## Prerequisites

Ensure you have the following installed on your system:

```bash
sudo apt install dpkg-dev
```

## Building the Package

Run the build script:

```bash
chmod +x build_deb.sh
./build_deb.sh
```

This will create a `.deb` file in the `build/` directory:

```
build/kapsulate_1.0.0_amd64.deb
```

## Installing the Package

Install the package using `dpkg`:

```bash
sudo dpkg -i build/kapsulate_1.0.0_amd64.deb
```

If there are missing dependencies, fix them with:

```bash
sudo apt-get install -f
```

## What Gets Installed

| Location                                                               | Content                                 |
| ---------------------------------------------------------------------- | --------------------------------------- |
| `/usr/bin/kapsulate`                                                   | Main executable wrapper script          |
| `/usr/share/kapsulate/`                                                | Python source code                      |
| `/usr/share/applications/kapsulate.desktop`                            | Desktop entry file                      |
| `/usr/share/autostart/kapsulate.desktop`                               | Autostart entry (system-level)          |
| `/usr/share/icons/hicolor/scalable/apps/kapsulate.svg`                 | Default icon                            |
| `/usr/share/icons/hicolor-dark/scalable/apps/kapsulate.svg`            | Dark theme icon                         |
| `/usr/share/icons/hicolor-light/scalable/apps/kapsulate.svg`           | Light theme icon                        |
| `/usr/share/doc/kapsulate/copyright`                                   | License and copyright information       |
| `/usr/share/metainfo/io.github.darkokuzmanovic.kapsulate.metainfo.xml` | AppStream metadata for software centers |
| `/etc/kapsulate/kapsulate.conf`                                        | Default configuration file              |
| `~/.local/share/kapsulate/logs/kapsulate.log`                          | Application logs (user-writable)        |
| `~/.config/kapsulate/kapsulate.conf`                                   | User-specific configuration (optional)  |

## Autostart Integration

The package installs a desktop entry to `/usr/share/autostart/` (system-level), which allows users to enable autostart via the tray menu:

1. Run Kapsulate from the application menu or terminal: `kapsulate`
2. Right-click the tray icon
3. Toggle "Start with system" to enable/disable autostart

When enabled, a symlink is created at `~/.config/autostart/kapsulate.desktop`.

## Uninstalling

Remove the package:

```bash
sudo dpkg -r kapsulate
```

To also remove configuration files:

```bash
sudo dpkg -P kapsulate
```

## Package Structure

The package follows the Debian Filesystem Hierarchy Standard:

```
kapsulate_1.0.0_amd64/
├── DEBIAN/
│   ├── control          # Package metadata
│   ├── postinst         # Post-installation script
│   └── prerm            # Pre-removal script
├── usr/
│   ├── bin/
│   │   └── kapsulate    # Main executable
│   └── share/
│       ├── applications/
│       │   └── kapsulate.desktop
│       ├── autostart/
│       │   └── kapsulate.desktop
│       ├── icons/
│       │   ├── hicolor/scalable/apps/kapsulate.svg
│       │   ├── hicolor-dark/scalable/apps/kapsulate.svg
│       │   └── hicolor-light/scalable/apps/kapsulate.svg
│       ├── doc/
│       │   └── kapsulate/
│       │       └── copyright
│       ├── metainfo/
│       │   └── io.github.darkokuzmanovic.kapsulate.metainfo.xml
│       └── kapsulate/
│           ├── main.py
│           ├── cli.py
│           ├── core/
│           ├── features/
│           ├── ui/
│           └── kapsulate.conf
└── etc/
    └── kapsulate/
        └── kapsulate.conf
```

## Dependencies

The package declares the following dependencies:

- `python3` - Python runtime
- `python3-pyqt6` - Qt6 Python bindings
- `keyd` - Keyboard remapping daemon
- `python3-dbus` - DBus Python bindings

These will be automatically installed by `apt` when you install the package.

## Troubleshooting

### Application won't start or PermissionError

If you see a `PermissionError` related to logs, ensure you have the latest version. Logs are now stored in `~/.local/share/kapsulate/logs/kapsulate.log`.

To view logs:

```bash
cat ~/.local/share/kapsulate/logs/kapsulate.log
```

### Autostart not working

1. Check if the symlink exists:

   ```bash
   ls -la ~/.config/autostart/kapsulate.desktop
   ```

2. Check if the desktop file is installed:

   ```bash
   ls -la /usr/share/applications/kapsulate.desktop
   ```

3. Enable autostart from the tray menu and check logs:
   ```bash
   journalctl -u kapsulate
   ```

### Application won't start

1. Check if all dependencies are installed:

   ```bash
   python3 -c "import PyQt6, dbus"
   ```

2. Check the wrapper script:

   ```bash
   /usr/bin/kapsulate
   ```

3. Check system logs:
   ```bash
   journalctl -xe
   ```
