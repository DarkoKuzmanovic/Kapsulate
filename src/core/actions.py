import subprocess
import shutil

class Actions:
    @staticmethod
    def run_command(cmd : list):
        try:
            subprocess.Popen(cmd)
        except FileNotFoundError:
            print(f"Command not found: {cmd}")
        except Exception as e:
            print(f"Error running command {cmd}: {e}")

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
        # Use KDialog to show a generated password? Or just copy to clipboard
        # For now, let's just use Python to generate and notification
        import secrets
        import string
        chars = string.ascii_letters + string.digits + "!@#$%^&*"
        pwd = "".join(secrets.choice(chars) for _ in range(16))
        
        # We need a way to copy to clipboard (wl-copy)
        try:
            subprocess.run(["wl-copy", pwd], check=True)
            return pwd
        except Exception as e:
            print(f"Clipboard error: {e}")
            return None

    @staticmethod
    def window_move_left():
        # trigger kwin shortcut? Or use wmctrl?
        # On Wayland, wmctrl doesn't work well.
        # Best to rely on KWin shortcuts directly mapped in keyd.
        # But if we need app logic...
        pass
