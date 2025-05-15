from PyQt6 import QtWidgets
from components.main_window import MainWindow
from components.splash_screen import SplashScreen
from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QFontDatabase, QFont
import os
from localization.language import Language

if __name__ == "__main__":
    import sys
    from PyQt6.QtCore import Qt

    app = QtWidgets.QApplication(sys.argv)

    # Register the Poppins font using relative paths
    base_path = os.path.dirname(__file__)
    QFontDatabase.addApplicationFont(os.path.join(base_path, "assets/fonts/Poppins/Poppins-Regular.ttf"))
    QFontDatabase.addApplicationFont(os.path.join(base_path, "assets/fonts/Poppins/Poppins-Bold.ttf"))
    QFontDatabase.addApplicationFont(os.path.join(base_path, "assets/fonts/Poppins/Poppins-Italic.ttf"))
    app.setFont(QFont("Poppins"))

    # Apply the theme stylesheet globally
    stylesheet_path = os.path.join(base_path, "styles/blue_theme.qss")
    with open(stylesheet_path, "r") as file:
        app.setStyleSheet(file.read())

    # Initialize language (default to English)
    language = Language()
    selected_language = "en"
    language.load_language(selected_language)

    # Show the splash screen
    splash_screen_duration = 0
    splash = SplashScreen()
    splash.show_splash(duration=splash_screen_duration)
    
    # Keep a reference to the main window
    def show_main_window():
        global main_window
        main_window = MainWindow(language)
        main_window.show()
        splash.close()

    QTimer.singleShot(splash_screen_duration, show_main_window)
    sys.exit(app.exec())
