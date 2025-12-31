import sys
import os
import signal
import subprocess
from PyQt6.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QMessageBox
from PyQt6.QtGui import QIcon, QAction, QDesktopServices
from PyQt6.QtCore import QTimer, QUrl, Qt, QObject, pyqtSlot
from PyQt6.QtDBus import QDBusConnection, QDBusInterface
from core.listener import KapsulateService, KapsulateServiceError
from core.logger import setup_logging, get_logger

# Application metadata
APP_VERSION = "1.0.0"
APP_AUTHOR = "Darko Kuzmanovic"
APP_WEBSITE = "https://github.com/DarkoKuzmanovic/Kapsulate"

# Base directory (parent of src/)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class KapsulateApp:
    def __init__(self):
        # Allow Ctrl+C to kill the app from terminal
        signal.signal(signal.SIGINT, signal.SIG_DFL)

        # Initialize logging
        self.logger = setup_logging(BASE_DIR)
        self.logger.info("Initializing KapsulateApp...")

        self.app = QApplication(sys.argv)
        self.app.setApplicationName("Kapsulate")
        self.app.setQuitOnLastWindowClosed(False)

        # Workaround for CTRL+C not working in PyQt
        self.timer = QTimer()
        self.timer.timeout.connect(lambda: None)
        self.timer.start(500)

        # Detect theme and load appropriate icon
        self._is_dark = self._detect_dark_theme()
        self._update_tray_icon()

        # Setup Tray Icon
        self.tray_icon = QSystemTrayIcon(self.app)
        self._apply_icon_to_tray()
        self.tray_icon.setToolTip("Kapsulate Running")

        # Listen for theme changes via DBus
        self._setup_theme_listener()
        try:
            self.service = KapsulateService()
        except KapsulateServiceError as e:
            self.logger.error(f"DBus Service failed: {e}")
            self._show_error("Kapsulate Error", str(e))

        # Context Menu
        self.menu = QMenu()

        # Open Config Action
        self.open_config_action = QAction("Open Config", self.menu)
        self.open_config_action.triggered.connect(self._open_config)
        self.menu.addAction(self.open_config_action)

        # Reload Config Action
        self.reload_action = QAction("Reload Config", self.menu)
        self.reload_action.triggered.connect(self._reload_config)
        self.menu.addAction(self.reload_action)

        self.menu.addSeparator()

        # About Action
        self.about_action = QAction("About Kapsulate", self.menu)
        self.about_action.triggered.connect(self._show_about)
        self.menu.addAction(self.about_action)

        # Autostart Action (only if installed via DEB)
        if self._is_autostart_available():
            self.autostart_action = QAction("Start with system", self.menu)
            self.autostart_action.setCheckable(True)
            self.autostart_action.setChecked(self._is_autostart_enabled())
            self.autostart_action.triggered.connect(self._toggle_autostart)
            self.menu.addAction(self.autostart_action)
            self.logger.debug("Autostart option available")
        else:
            self.logger.debug("Autostart not available (not installed via DEB)")

        self.menu.addSeparator()

        # Quit Action
        self.quit_action = QAction("Quit", self.menu)
        self.quit_action.triggered.connect(self.app.quit)
        self.menu.addAction(self.quit_action)

        self.tray_icon.setContextMenu(self.menu)
        self.tray_icon.show()

        # Startup Notification
        self.tray_icon.showMessage(
            "Kapsulate",
            "Service Started Successfully",
            QSystemTrayIcon.MessageIcon.Information,
            3000
        )

    def _open_config(self):
        # Try system config first (installed package)
        config_path = "/etc/kapsulate/kapsulate.conf"
        if not os.path.exists(config_path):
            # Try user config directory
            config_path = os.path.expanduser("~/.config/kapsulate/kapsulate.conf")
        if not os.path.exists(config_path):
            # Fall back to local config (development mode)
            config_path = os.path.join(BASE_DIR, "config", "kapsulate.conf")

        if os.path.exists(config_path):
            self.logger.info(f"Opening config: {config_path}")
            QDesktopServices.openUrl(QUrl.fromLocalFile(config_path))
        else:
            self.logger.error(f"Config file not found: {config_path}")
            self._show_error("Error", "Config file not found!")

    def _reload_config(self):
        """Reload keyd configuration by restarting the keyd service."""
        self.logger.info("Reloading keyd configuration...")
        try:
            # keyd requires root to restart, use pkexec for GUI prompt
            result = subprocess.run(
                ["pkexec", "systemctl", "restart", "keyd"],
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode == 0:
                self.logger.info("keyd service restarted successfully")
                self.tray_icon.showMessage(
                    "Kapsulate",
                    "keyd service restarted successfully",
                    QSystemTrayIcon.MessageIcon.Information,
                    2000
                )
            else:
                self.logger.error(f"Failed to restart keyd: {result.stderr.strip()}")
                self._show_error("Error", f"Failed to restart keyd: {result.stderr.strip()}")
        except subprocess.TimeoutExpired:
            self.logger.error("Timeout waiting for keyd restart")
            self._show_error("Error", "Timeout waiting for keyd restart")
        except FileNotFoundError:
            self.logger.error("pkexec not found")
            self._show_error("Error", "pkexec not found. Cannot restart keyd.")
        except Exception as e:
            self.logger.error(f"Failed to reload: {e}")
            self._show_error("Error", f"Failed to reload: {e}")

    def _update_tray_icon(self):
        """Update icon path based on current theme."""
        icon_variant = "hicolor-dark" if self._is_dark else "hicolor-light"

        # Try system icon paths first (installed package)
        system_icon_path = f"/usr/share/icons/{icon_variant}/scalable/apps/kapsulate.svg"
        if os.path.exists(system_icon_path):
            self._icon_path = system_icon_path
        else:
            # Fall back to local assets (development mode)
            self._icon_path = os.path.join(BASE_DIR, "assets", icon_variant, "scalable", "apps", "kapsulate.svg")

    def _apply_icon_to_tray(self):
        """Apply the current icon to the tray."""
        if os.path.exists(self._icon_path):
            icon = QIcon(self._icon_path)
            self.tray_icon.setIcon(icon)
        else:
            self.logger.warning(f"Icon not found at {self._icon_path}, using fallback")
            icon = self.app.style().standardIcon(self.app.style().StandardPixmap.SP_ComputerIcon)
            self.tray_icon.setIcon(icon)

    def _setup_theme_listener(self):
        """Listen for theme changes via periodic polling."""
        # Check theme every 5 seconds
        self._theme_check_timer = QTimer()
        self._theme_check_timer.timeout.connect(self._check_theme_change)
        self._theme_check_timer.start(5000)
        self.logger.info("Listening for theme changes (polling)")

    def _check_theme_change(self):
        """Check if theme has changed and update icon if needed."""
        new_is_dark = self._detect_dark_theme()
        if new_is_dark != self._is_dark:
            self._is_dark = new_is_dark
            self.logger.info(f"Theme changed to: {'dark' if self._is_dark else 'light'}")
            self._update_tray_icon()
            self._apply_icon_to_tray()

    def _on_theme_changed(self, message):
        """Handle theme change signal from DBus."""
        args = message.arguments() if isinstance(message, QDBusMessage) else [message]

        # Check if this is the color-scheme setting
        if len(args) >= 2:
            namespace = args[0] if len(args) > 0 else ""
            key = args[1] if len(args) > 1 else ""

            if namespace == "org.freedesktop.appearance" and key == "color-scheme":
                value = args[2] if len(args) > 2 else 0
                new_is_dark = int(value) == 1

                if new_is_dark != self._is_dark:
                    self._is_dark = new_is_dark
                    self.logger.info(f"Theme changed to: {'dark' if self._is_dark else 'light'}")
                    self._update_tray_icon()
                    self._apply_icon_to_tray()

    def _detect_dark_theme(self):
        """Check if the system is using a dark theme via freedesktop portal."""
        try:
            interface = QDBusInterface(
                "org.freedesktop.portal.Desktop",
                "/org/freedesktop/portal/desktop",
                "org.freedesktop.portal.Settings",
                QDBusConnection.sessionBus()
            )

            if interface.isValid():
                reply = interface.call("Read", "org.freedesktop.appearance", "color-scheme")
                if reply.arguments():
                    # color-scheme: 0 = no preference, 1 = dark, 2 = light
                    is_dark = int(reply.arguments()[0]) == 1
                    self.logger.debug(f"Theme detected: {'dark' if is_dark else 'light'}")
                    return is_dark
        except Exception as e:
            self.logger.warning(f"Theme detection failed: {e}")

        # Default to dark theme (most common for KDE)
        return True

    def _show_error(self, title, message):
        """Show error notification via tray icon."""
        self.logger.error(f"{title}: {message}")
        if hasattr(self, 'tray_icon') and self.tray_icon:
            self.tray_icon.showMessage(
                title,
                message,
                QSystemTrayIcon.MessageIcon.Warning,
                5000
            )

    def _show_about(self):
        """Show the About dialog."""
        about_text = f"""<h2>Kapsulate</h2>
<p><b>Version:</b> {APP_VERSION}</p>
<p><b>Author:</b> {APP_AUTHOR}</p>
<p>A keyboard-driven productivity utility for KDE Plasma.</p>
<p><a href="{APP_WEBSITE}">GitHub Repository</a></p>
<hr>
<p><small>Built with PyQt6 and keyd</small></p>"""

        about_box = QMessageBox()
        about_box.setWindowTitle("About Kapsulate")
        about_box.setTextFormat(Qt.TextFormat.RichText)
        about_box.setText(about_text)
        about_box.setIcon(QMessageBox.Icon.Information)
        about_box.exec()

    def _is_autostart_available(self):
        """Check if autostart is available (DEB installed)."""
        system_desktop = "/usr/share/applications/kapsulate.desktop"
        return os.path.exists(system_desktop)

    def _is_autostart_enabled(self):
        """Check if autostart is enabled for current user."""
        autostart_path = os.path.expanduser("~/.config/autostart/kapsulate.desktop")
        return os.path.exists(autostart_path)

    def _toggle_autostart(self, enabled):
        """Enable or disable autostart for current user."""
        autostart_dir = os.path.expanduser("~/.config/autostart")
        autostart_path = os.path.join(autostart_dir, "kapsulate.desktop")
        system_desktop = "/usr/share/applications/kapsulate.desktop"

        if enabled:
            os.makedirs(autostart_dir, exist_ok=True)
            try:
                os.symlink(system_desktop, autostart_path)
                self.logger.info("Autostart enabled")
                self.tray_icon.showMessage(
                    "Kapsulate",
                    "Autostart enabled",
                    QSystemTrayIcon.MessageIcon.Information,
                    2000
                )
            except OSError as e:
                self.logger.error(f"Failed to enable autostart: {e}")
                self._show_error("Error", f"Failed to enable autostart: {e}")
                # Revert the checkbox state
                self.autostart_action.setChecked(False)
        else:
            if os.path.exists(autostart_path):
                try:
                    os.remove(autostart_path)
                    self.logger.info("Autostart disabled")
                    self.tray_icon.showMessage(
                        "Kapsulate",
                        "Autostart disabled",
                        QSystemTrayIcon.MessageIcon.Information,
                        2000
                    )
                except OSError as e:
                    self.logger.error(f"Failed to disable autostart: {e}")
                    self._show_error("Error", f"Failed to disable autostart: {e}")
                    # Revert the checkbox state
                    self.autostart_action.setChecked(True)

    def run(self):
        self.logger.info("Starting event loop...")
        sys.exit(self.app.exec())

if __name__ == "__main__":
    kapsulate = KapsulateApp()
    kapsulate.run()
