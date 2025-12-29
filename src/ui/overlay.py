from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont
from core.logger import get_logger

class OSD(QWidget):
    def __init__(self):
        super().__init__()
        self.logger = get_logger()
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | 
            Qt.WindowType.WindowStaysOnTopHint | 
            Qt.WindowType.Tool |
            Qt.WindowType.X11BypassWindowManagerHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)

        # Style
        self._layout = QVBoxLayout()
        self._label = QLabel("Kapsulate")
        self._label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        font = QFont("Sans Serif", 24, QFont.Weight.Bold)
        self._label.setFont(font)
        self._label.setStyleSheet("color: white;")
        
        self._layout.addWidget(self._label)
        self.setLayout(self._layout)

        # Background
        self.setStyleSheet("""
            background-color: rgba(0, 0, 0, 180);
            border-radius: 15px;
            padding: 20px;
        """)

        self._hide_timer = QTimer()
        self._hide_timer.setSingleShot(True)
        self._hide_timer.timeout.connect(self.hide)

    def show_message(self, text, duration=1500):
        self.logger.debug(f"OSD Message: {text}")
        self._label.setText(text)
        self.adjustSize()
        
        # Center on screen (rough approximation, can be improved)
        screen = self.screen()
        if screen:
            screen_geo = screen.geometry()
            x = (screen_geo.width() - self.width()) // 2
            y = (screen_geo.height() - self.height()) * 0.8
            self.move(int(x), int(y))
        
        self.show()
        self._hide_timer.start(duration)

_osd_instance = None

def get_osd():
    global _osd_instance
    if _osd_instance is None:
        _osd_instance = OSD()
    return _osd_instance
