from PyQt6.QtWidgets import QSplashScreen, QLabel, QVBoxLayout, QWidget
from PyQt6.QtGui import QGuiApplication
from PyQt6.QtCore import Qt, QTimer
from config.constants import PROGRAM_NAME, AUTHOR_NAME, COMPANY_NAME
import os

class SplashScreen(QSplashScreen):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Dialog)
        self.setFixedSize(400, 200)

        # Load the stylesheet for the splash screen
        base_path = os.path.dirname(__file__)
        stylesheet_path = os.path.join(base_path, "../styles/splash_screen.qss")
        with open(stylesheet_path, "r") as file:
            self.setStyleSheet(file.read())

        # Center the splash screen on the screen
        screen_geometry = QGuiApplication.primaryScreen().geometry()
        self.move(
            screen_geometry.center().x() - self.width() // 2,
            screen_geometry.center().y() - self.height() // 2
        )

        # Create content for the splash screen
        content = QWidget(self)
        layout = QVBoxLayout(content)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        app_name_label = QLabel(PROGRAM_NAME)
        app_name_label.setObjectName("appNameLabel")  # Set object name for styling
        layout.addWidget(app_name_label)

        by_label = QLabel(f"By {COMPANY_NAME}")
        by_label.setObjectName("companyLabel")  # Set object name for styling
        layout.addWidget(by_label)

        author_label = QLabel(AUTHOR_NAME)
        author_label.setObjectName("authorLabel")  # Set object name for styling
        layout.addWidget(author_label)

        content.setLayout(layout)
        content.setGeometry(0, 0, 400, 200)

    def show_splash(self, duration=3000):
        self.show()
        QTimer.singleShot(duration, self.close)