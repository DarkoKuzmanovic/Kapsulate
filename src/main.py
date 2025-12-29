import sys
import os
import signal
import subprocess
from PyQt6.QtWidgets import QApplication, QSystemTrayIcon, QMenu
from PyQt6.QtGui import QIcon, QAction, QDesktopServices
from PyQt6.QtCore import QTimer, QUrl
from PyQt6.QtDBus import QDBusConnection, QDBusInterface
from core.listener import KapsulateService, KapsulateServiceError
from core.logger import setup_logging, get_logger

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
        self.app.setAccountName("Kapsulate")
        self.app.setApplicationName("Kapsulate")
        self.app.setQuitOnLastWindowClosed(False)

        # Workaround for CTRL+C not working in PyQt
        self.timer = QTimer()
        self.timer.timeout.connect(lambda: None)
        self.timer.start(500)

        # Detect theme and load appropriate icon
        is_dark = self._is_dark_theme()
        icon_variant = "hicolor-dark" if is_dark else "hicolor-light"
        icon_path = os.path.join(BASE_DIR, "assets", icon_variant, "scalable", "apps", "kapsulate.svg")

        # Setup Tray Icon
        self.tray_icon = QSystemTrayIcon(self.app)
        
        if os.path.exists(icon_path):
            icon = QIcon(icon_path)
            self.tray_icon.setIcon(icon)
        else:
            self.logger.warning(f"Icon not found at {icon_path}, using fallback")
            icon = self.app.style().standardIcon(self.app.style().StandardPixmap.SP_ComputerIcon)
            self.tray_icon.setIcon(icon)
        
        self.tray_icon.setToolTip("Kapsulate Running")

        # Initialize DBus Service
        try:
            self.service = KapsulateService()
        except KapsulateServiceError as e:
            self.logger.error(f"DBus Service failed: {e}")
            self.tray_icon.showMessage(
                "Kapsulate Error",
                str(e),
                QSystemTrayIcon.MessageIcon.Critical,
                5000
            )

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
        config_path = os.path.join(BASE_DIR, "config", "kapsulate.conf")
        if os.path.exists(config_path):
            self.logger.info(f"Opening config: {config_path}")
            QDesktopServices.openUrl(QUrl.fromLocalFile(config_path))
        else:
            self.logger.error(f"Config file not found: {config_path}")
            self.tray_icon.showMessage("Error", "Config file not found!", QSystemTrayIcon.MessageIcon.Warning, 3000)

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
                self.tray_icon.showMessage(
                    "Error",
                    f"Failed to restart keyd: {result.stderr.strip()}",
                    QSystemTrayIcon.MessageIcon.Warning,
                    3000
                )
        except subprocess.TimeoutExpired:
            self.logger.error("Timeout waiting for keyd restart")
            self.tray_icon.showMessage(
                "Error",
                "Timeout waiting for keyd restart",
                QSystemTrayIcon.MessageIcon.Warning,
                3000
            )
        except FileNotFoundError:
            self.logger.error("pkexec not found")
            self.tray_icon.showMessage(
                "Error",
                "pkexec not found. Cannot restart keyd.",
                QSystemTrayIcon.MessageIcon.Warning,
                3000
            )
        except Exception as e:
            self.logger.error(f"Failed to reload: {e}")
            self.tray_icon.showMessage(
                "Error",
                f"Failed to reload: {e}",
                QSystemTrayIcon.MessageIcon.Warning,
                3000
            )

    def _is_dark_theme(self):
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

    def run(self):
        self.logger.info("Starting event loop...")
        sys.exit(self.app.exec())

if __name__ == "__main__":
    kapsulate = KapsulateApp()
    kapsulate.run()
