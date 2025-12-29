from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QColor, QPalette, QFont

class OSD(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | 
            Qt.WindowType.WindowStaysOnTopHint | 
            Qt.WindowType.Tool |
            Qt.WindowType.X11BypassWindowManagerHint # Helps on some WMs
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)

        # Style
        self.layout = QVBoxLayout()
        self.label = QLabel("Kapsulate")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        font = QFont("Sans Serif", 24, QFont.Weight.Bold)
        self.label.setFont(font)
        self.label.setStyleSheet("color: white;")
        
        self.layout.addWidget(self.label)
        self.setLayout(self.layout)

        # Background
        self.setStyleSheet("""
            background-color: rgba(0, 0, 0, 180);
            border-radius: 15px;
            padding: 20px;
        """)

        self.hide_timer = QTimer()
        self.hide_timer.setSingleShot(True)
        self.hide_timer.timeout.connect(self.hide)

    def show_message(self, text, duration=1500):
        self.label.setText(text)
        self.adjustSize()
        
        # Center on screen (rough approximation, can be improved)
        screen = self.screen()
        if screen:
            screen_geo = screen.geometry()
            x = (screen_geo.width() - self.width()) // 2
            y = (screen_geo.height() - self.height()) * 0.8
            self.move(int(x), int(y))
        
        self.show()
        self.hide_timer.start(duration)

_osd_instance = None

def get_osd():
    global _osd_instance
    if _osd_instance is None:
        _osd_instance = OSD()
    return _osd_instance
