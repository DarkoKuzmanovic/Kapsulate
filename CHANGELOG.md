# Changelog

All notable changes to Kapsulate will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- System startup integration with "Start with system" tray menu option
- DEB packaging support for easy installation on Debian-based systems
- GitHub Actions workflow for automated release builds

### Fixed

- Permission error when running installed DEB package (logs now stored in `~/.local/share/kapsulate/logs/`)
- Config file path resolution for installed packages
- Icon path resolution for installed packages

## [1.0.0] - 2025-12-30

### Added

- Initial release of Kapsulate
- System tray interface for KDE Plasma
- Text overlay capabilities
- Keyd configuration management
- Theme-aware tray icons (dark/light mode)
- DBus integration for theme change detection
- About dialog
- Error notification system

### Fixed

- Hardcoded relative paths
- DBus registration failure handling
- Blocking `time.sleep()` replaced with Qt timers
- Null check for screen in OSD
- Password feedback to user

### Improved

- Proper logging system
- Code quality improvements
- Consistent method naming convention
- Named constants for magic numbers
