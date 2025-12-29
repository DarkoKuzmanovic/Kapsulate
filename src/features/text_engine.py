import subprocess
import time
from PyQt6.QtCore import QObject, pyqtSignal, QThread
from evdev import UInput, ecodes as e

# Constants for delays
KEY_PRESS_DELAY = 0.05
CLIPBOARD_SYNC_DELAY = 0.1

class TransformationWorker(QObject):
    finished = pyqtSignal(str)  # Emits the transformed text or None
    error = pyqtSignal(str)

    def __init__(self, mode):
        super().__init__()
        self.mode = mode

    def run(self):
        try:
            with UInput() as ui:
                # 1. Simulate Ctrl+C
                ui.write(e.EV_KEY, e.KEY_LEFTCTRL, 1)
                ui.write(e.EV_KEY, e.KEY_C, 1)
                ui.syn()
                QThread.msleep(int(KEY_PRESS_DELAY * 1000))
                ui.write(e.EV_KEY, e.KEY_C, 0)
                ui.write(e.EV_KEY, e.KEY_LEFTCTRL, 0)
                ui.syn()

                # Give it a moment to copy
                QThread.msleep(int(CLIPBOARD_SYNC_DELAY * 1000))
                
                original = self.get_clipboard()
                if not original:
                    self.finished.emit(None)
                    return

                transformed = self.transform_case(original, self.mode)
                if transformed != original:
                    self.set_clipboard(transformed)
                    # Give it a moment to set clipboard
                    QThread.msleep(int(KEY_PRESS_DELAY * 1000))
                    
                    # 2. Simulate Ctrl+V
                    ui.write(e.EV_KEY, e.KEY_LEFTCTRL, 1)
                    ui.write(e.EV_KEY, e.KEY_V, 1)
                    ui.syn()
                    QThread.msleep(int(KEY_PRESS_DELAY * 1000))
                    ui.write(e.EV_KEY, e.KEY_V, 0)
                    ui.write(e.EV_KEY, e.KEY_LEFTCTRL, 0)
                    ui.syn()
                    
                    self.finished.emit(transformed)
                else:
                    self.finished.emit(None)

        except PermissionError:
            self.error.emit("Permission denied for UInput (check 'input' group)")
        except Exception as ex:
            self.error.emit(f"Error: {ex}")

    def get_clipboard(self):
        try:
            return subprocess.check_output(["wl-paste", "-n"], text=True)
        except:
            return ""

    def set_clipboard(self, text):
        try:
            p = subprocess.Popen(["wl-copy", "-n"], stdin=subprocess.PIPE, text=True)
            p.communicate(input=text)
        except:
            pass

    def transform_case(self, text, mode):
        if mode == "upper": return text.upper()
        if mode == "lower": return text.lower()
        if mode == "title": return text.title()
        if mode == "camel":
            parts = text.replace("-", " ").replace("_", " ").split()
            if not parts: return ""
            return parts[0].lower() + "".join(p.capitalize() for p in parts[1:])
        return text

class TextEngine:
    """Wrapper to run transformation in a separate thread."""
    @staticmethod
    def process_selection(mode, on_finished):
        thread = QThread()
        worker = TransformationWorker(mode)
        worker.moveToThread(thread)
        
        thread.started.connect(worker.run)
        worker.finished.connect(lambda res: on_finished(res))
        worker.finished.connect(thread.quit)
        worker.finished.connect(worker.deleteLater)
        thread.finished.connect(thread.deleteLater)
        
        # Keep references to prevent GC
        TextEngine._active_threads = getattr(TextEngine, "_active_threads", [])
        TextEngine._active_threads.append((thread, worker))
        
        # Cleanup routine
        def cleanup():
            if (thread, worker) in TextEngine._active_threads:
                TextEngine._active_threads.remove((thread, worker))
        
        thread.finished.connect(cleanup)
        thread.start()
