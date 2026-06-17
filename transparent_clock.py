import sys
import os
from PyQt6.QtWidgets import QApplication, QLabel, QWidget, QVBoxLayout
from PyQt6.QtCore import Qt, QTimer, QTime, QSettings
from PyQt6.QtGui import QFont, QFontDatabase

class DeskletClock(QWidget):
    def __init__(self):
        super().__init__()

        # Force the program to set the script's directory as the base working directory
        os.chdir(os.path.dirname(os.path.abspath(__file__)))

        # 1. Window settings and prevent disappearing
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnBottomHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_X11NetWmWindowTypeDesktop)
        self.setAttribute(Qt.WidgetAttribute.WA_AlwaysStackOnTop, False)
        
        # Memory setup to save the clock's position
        self.settings = QSettings("config.ini", QSettings.Format.IniFormat)
        
        pos = self.settings.value("pos", (500, 200))
        try:
            self.move(int(pos[0]), int(pos[1]))
        except (TypeError, IndexError):
            self.move(500, 200)
        
        self.old_pos = None

        # 2. Create and style the text (Label)
        self.label = QLabel()
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        font_id = QFontDatabase.addApplicationFont("Font/Poppins-Black.ttf")
        families = QFontDatabase.applicationFontFamilies(font_id)
        
        if families:
            font_family = families[0]
            self.label.setFont(QFont(font_family, 150))
        else:
            font = QFont("Poppins", 150)
            font.setWeight(900)
            font.setBold(True)
            self.label.setFont(font)
            
        self.label.setStyleSheet("color: rgba(255, 255, 255, 100);")

        # 3. Layout organization
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        # 4. Smart timer (Accurate and very energy-efficient update)
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_time)
        
        # First update immediately upon running
        self.update_time()

        self.resize(600, 300)

    def update_time(self):
        # Update the text with the current time
        current_time = QTime.currentTime()
        self.label.setText(current_time.toString("HH:mm"))
        
        # Calculate how many seconds and milliseconds are remaining to reach the next minute accurately
        # This allows the code to completely sleep and consume 0% CPU until a new minute starts
        msec_to_next_minute = (60 - current_time.second()) * 1000 - current_time.msec()
        self.timer.start(msec_to_next_minute)

    def closeEvent(self, event):
        self.settings.setValue("pos", (self.x(), self.y()))
        self.settings.sync()
        event.accept()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.old_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        if self.old_pos is not None:
            delta = event.globalPosition().toPoint() - self.old_pos
            new_x = self.x() + delta.x()
            new_y = self.y() + delta.y()
            
            screen = self.screen().availableGeometry()
            new_x = max(0, min(new_x, screen.width() - self.width()))
            new_y = max(0, min(new_y, screen.height() - self.height()))
            
            self.move(new_x, new_y)
            self.old_pos = event.globalPosition().toPoint()

    def mouseReleaseEvent(self, event):
        self.old_pos = None
        self.settings.setValue("pos", (self.x(), self.y()))
        self.settings.sync()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    clock = DeskletClock()
    clock.show()
    sys.exit(app.exec())

