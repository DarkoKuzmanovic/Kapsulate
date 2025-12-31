import subprocess
from PyQt6.QtCore import QObject, pyqtSignal, QThread
from evdev import UInput, ecodes as e
from core.logger import get_logger
from ui.overlay import get_osd

# Constants for delays (in milliseconds)
KEY_PRESS_DELAY_MS = 50
CLIPBOARD_SYNC_DELAY_MS = 100

# Maximum number of active threads to keep in memory
MAX_ACTIVE_THREADS = 10

class TransformationWorker(QObject):
    finished = pyqtSignal(str)  # Emits the transformed text or None
    error = pyqtSignal(str)

    def __init__(self, mode):
        super().__init__()
        self.mode = mode
        self.logger = get_logger()

    def run(self):
        try:
            with UInput() as ui:
                self.logger.debug(f"Simulating Ctrl+C for {self.mode} transform")
                # 1. Simulate Ctrl+C
                ui.write(e.EV_KEY, e.KEY_LEFTCTRL, 1)
                ui.write(e.EV_KEY, e.KEY_C, 1)
                ui.syn()
                QThread.msleep(KEY_PRESS_DELAY_MS)
                ui.write(e.EV_KEY, e.KEY_C, 0)
                ui.write(e.EV_KEY, e.KEY_LEFTCTRL, 0)
                ui.syn()

                # Give it a moment to copy
                QThread.msleep(CLIPBOARD_SYNC_DELAY_MS)

                original = self._get_clipboard()
                if not original:
                    self.logger.warning("Clipboard empty after Ctrl+C simulation")
                    self.finished.emit(None)
                    return

                transformed = self._transform_case(original, self.mode)
                if transformed != original:
                    self._set_clipboard(transformed)
                    # Give it a moment to set clipboard
                    QThread.msleep(KEY_PRESS_DELAY_MS)

                    self.logger.debug("Simulating Ctrl+V for paste")
                    # 2. Simulate Ctrl+V
                    ui.write(e.EV_KEY, e.KEY_LEFTCTRL, 1)
                    ui.write(e.EV_KEY, e.KEY_V, 1)
                    ui.syn()
                    QThread.msleep(KEY_PRESS_DELAY_MS)
                    ui.write(e.EV_KEY, e.KEY_V, 0)
                    ui.write(e.EV_KEY, e.KEY_LEFTCTRL, 0)
                    ui.syn()

                    self.finished.emit(transformed)
                else:
                    self.logger.debug("Text already in target case, skipping paste")
                    self.finished.emit(None)

        except PermissionError:
            self.logger.error("Permission denied for UInput. User must be in 'input' group.")
            self.error.emit("Permission denied for UInput (check 'input' group)")
        except Exception as ex:
            self.logger.exception(f"Unexpected error in TransformationWorker: {ex}")
            self.error.emit(f"Error: {ex}")

    def _get_clipboard(self):
        try:
            return subprocess.check_output(["wl-paste", "-n"], text=True)
        except Exception as e:
            self.logger.error(f"Failed to get clipboard: {e}")
            return ""

    def _set_clipboard(self, text):
        try:
            p = subprocess.Popen(["wl-copy", "-n"], stdin=subprocess.PIPE, text=True)
            p.communicate(input=text)
        except Exception as e:
            self.logger.error(f"Failed to set clipboard: {e}")

    def _transform_case(self, text, mode):
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
        logger = get_logger()
        logger.debug(f"Process selection triggered with mode: {mode}")

        thread = QThread()
        worker = TransformationWorker(mode)
        worker.moveToThread(thread)

        thread.started.connect(worker.run)
        worker.finished.connect(lambda res: on_finished(res))

        # Log errors and show OSD notification to user
        def handle_error(err):
            logger.error(f"TextEngine Worker error: {err}")
            try:
                get_osd().show_message("Transformation Failed")
            except Exception as osd_err:
                logger.warning(f"Failed to show OSD error: {osd_err}")

        worker.error.connect(handle_error)

        worker.finished.connect(thread.quit)
        worker.finished.connect(worker.deleteLater)
        thread.finished.connect(thread.deleteLater)

        # Keep references to prevent GC with bounded list
        TextEngine._active_threads = getattr(TextEngine, "_active_threads", [])

        # Limit the list size to prevent unbounded growth
        if len(TextEngine._active_threads) >= MAX_ACTIVE_THREADS:
            # Remove oldest finished threads
            TextEngine._active_threads = [
                (t, w) for t, w in TextEngine._active_threads
                if t.isRunning()
            ][:MAX_ACTIVE_THREADS - 1]

        TextEngine._active_threads.append((thread, worker))

        # Cleanup routine with error handling
        def cleanup():
            try:
                if (thread, worker) in TextEngine._active_threads:
                    TextEngine._active_threads.remove((thread, worker))
            except (ValueError, RuntimeError) as e:
                logger.debug(f"Thread cleanup note: {e}")

        thread.finished.connect(cleanup)
        thread.start()
