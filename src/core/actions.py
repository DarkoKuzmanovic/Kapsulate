import subprocess
import shutil
import secrets
import string
from .logger import get_logger

class Actions:
    @staticmethod
    def run_command(cmd: list):
        logger = get_logger()
        try:
            logger.debug(f"Running command: {cmd}")
            subprocess.Popen(cmd)
        except FileNotFoundError:
            logger.error(f"Command not found: {cmd[0] if cmd else 'empty command'}")
        except PermissionError:
            logger.error(f"Permission denied executing command: {cmd}")
        except OSError as e:
            logger.error(f"OS error running command {cmd}: {e}")
        except Exception as e:
            logger.exception(f"Unexpected error running command {cmd}: {e}")

    @staticmethod
    def open_task_manager():
        # Try ksysguard, then plasma-systemmonitor, then gnome-system-monitor
        monitors = ["plasma-systemmonitor", "ksysguard", "gnome-system-monitor", "htop"]
        for m in monitors:
            if shutil.which(m):
                if m == "htop":
                    Actions.run_command(["konsole", "-e", "htop"])
                else:
                    Actions.run_command([m])
                return

    @staticmethod
    def open_color_picker():
        # kcolorchooser is standard in KDE
        Actions.run_command(["kcolorchooser"])

    @staticmethod
    def open_password_gen():
        logger = get_logger()
        chars = string.ascii_letters + string.digits + "!@#$%^&*"
        pwd = "".join(secrets.choice(chars) for _ in range(16))

        # We need a way to copy to clipboard (wl-copy)
        try:
            subprocess.run(["wl-copy", pwd], check=True)
            logger.debug("Password generated and copied to clipboard")
            return pwd
        except Exception as e:
            logger.error(f"Clipboard error (is wl-clipboard installed?): {e}")
            return None
