from PyQt6.QtCore import QObject, pyqtSlot
from PyQt6.QtDBus import QDBusConnection
from .actions import Actions
from features.text_engine import TextEngine
from ui.overlay import get_osd


class KapsulateServiceError(Exception):
    """Raised when the Kapsulate DBus service fails to initialize."""
    pass


class KapsulateService(QObject):
    def __init__(self):
        super().__init__()
        
        # Connect to Session Bus and register service
        if not QDBusConnection.sessionBus().registerService('org.kapsulate.service'):
            raise KapsulateServiceError(
                "Failed to register DBus service. Is another instance running?"
            )
        
        # Register this object and export all slots
        if not QDBusConnection.sessionBus().registerObject(
            '/org/kapsulate/Service', 
            self, 
            QDBusConnection.RegisterOption.ExportAllSlots
        ):
            raise KapsulateServiceError("Failed to register DBus object")

    @pyqtSlot()
    def TriggerTaskManager(self):
        print("Triggering Task Manager")
        Actions.open_task_manager()

    @pyqtSlot()
    def TriggerColorPicker(self):
        print("Triggering Color Picker")
        Actions.open_color_picker()

    @pyqtSlot()
    def TriggerPassword(self):
        print("Triggering Password")
        pwd = Actions.open_password_gen()
        if pwd:
            get_osd().show_message("Password copied!")
        else:
            get_osd().show_message("Failed to generate password")

    @pyqtSlot()
    def TriggerExpand(self):
        print("Triggering Expand")
        get_osd().show_message("Expanding...")
        # TODO: Implement full expansion logic later
        # For now, just a demo
        
    @pyqtSlot(str)
    def TriggerTransform(self, mode):
        print(f"Triggering Transform: {mode}")
        
        def on_finished(res):
            if res:
                get_osd().show_message(f"Converted to {mode}")
            else:
                get_osd().show_message("Transformation Failed")

        TextEngine.process_selection(mode, on_finished)


