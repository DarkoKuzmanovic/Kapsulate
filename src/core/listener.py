from PyQt6.QtCore import QObject, pyqtSlot
from PyQt6.QtDBus import QDBusConnection
from .actions import Actions
from .logger import get_logger
from features.text_engine import TextEngine
from ui.overlay import get_osd

class KapsulateServiceError(Exception):
    """Raised when the Kapsulate DBus service fails to initialize."""
    pass

class KapsulateService(QObject):
    def __init__(self):
        super().__init__()
        self.logger = get_logger()
        
        # Connect to Session Bus and register service
        if not QDBusConnection.sessionBus().registerService('org.kapsulate.service'):
            self.logger.error("Failed to register DBus service org.kapsulate.service")
            raise KapsulateServiceError(
                "Failed to register DBus service. Is another instance running?"
            )
        
        # Register this object and export all slots
        if not QDBusConnection.sessionBus().registerObject(
            '/org/kapsulate/Service', 
            self, 
            QDBusConnection.RegisterOption.ExportAllSlots
        ):
            self.logger.error("Failed to register DBus object")
            raise KapsulateServiceError("Failed to register DBus object")
        
        self.logger.info("DBus service 'org.kapsulate.service' registered.")

    @pyqtSlot()
    def TriggerTaskManager(self):
        self.logger.info("Triggering Task Manager")
        Actions.open_task_manager()

    @pyqtSlot()
    def TriggerColorPicker(self):
        self.logger.info("Triggering Color Picker")
        Actions.open_color_picker()

    @pyqtSlot()
    def TriggerPassword(self):
        self.logger.info("Triggering Password generation")
        pwd = Actions.open_password_gen()
        if pwd:
            get_osd().show_message("Password copied!")
        else:
            get_osd().show_message("Failed to generate password")

    @pyqtSlot()
    def TriggerExpand(self):
        self.logger.info("Triggering Text Expansion snippet")
        get_osd().show_message("Expanding...")
        # TODO: Implement full expansion logic later
        
    @pyqtSlot(str)
    def TriggerTransform(self, mode):
        self.logger.info(f"Triggering Text Transformation: {mode}")
        
        def on_finished(res):
            if res:
                self.logger.debug(f"Transformation to {mode} successful")
                get_osd().show_message(f"Converted to {mode}")
            else:
                self.logger.warning(f"Transformation to {mode} failed or no change")
                get_osd().show_message("Transformation Failed")

        TextEngine.process_selection(mode, on_finished)


