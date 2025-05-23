import os
from PyQt6 import QtWidgets
from components.main_window import MainWindow
from components.splash_screen import SplashScreen
from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QFontDatabase, QFont
import os
from localization.language import Language
import sys

if __name__ == "__main__":
    from PyQt6.QtCore import Qt

    # Define base_path before using it
    base_path = os.path.dirname(__file__)
    LANGUAGE_FILE = os.path.join(base_path, "config", "language.txt")  # Path to the language file

    def read_language_from_file():
        """Read the selected language from the file."""
        if os.path.exists(LANGUAGE_FILE):
            with open(LANGUAGE_FILE, "r", encoding="utf-8") as file:
                return file.read().strip()
        return "en"  # Default to English if the file doesn't exist

    def write_language_to_file(language_code):
        """Write the selected language to the file."""
        with open(LANGUAGE_FILE, "w", encoding="utf-8") as file:
            file.write(language_code)

    # Parse the language argument if provided
    selected_language = read_language_from_file()
    for arg in sys.argv:
        if arg.startswith("--language="):
            selected_language = arg.split("=")[1]
            write_language_to_file(selected_language)  # Save the language to the file

    app = QtWidgets.QApplication(sys.argv)

    # Register the Poppins font using relative paths
    QFontDatabase.addApplicationFont(os.path.join(base_path, "assets/fonts/Poppins/Poppins-Regular.ttf"))
    QFontDatabase.addApplicationFont(os.path.join(base_path, "assets/fonts/Poppins/Poppins-Bold.ttf"))
    QFontDatabase.addApplicationFont(os.path.join(base_path, "assets/fonts/Poppins/Poppins-Italic.ttf"))
    app.setFont(QFont("Poppins"))

    # Apply the theme stylesheet globally
    stylesheet_path = os.path.join(base_path, "styles/blue_theme.qss")
    with open(stylesheet_path, "r") as file:
        app.setStyleSheet(file.read())

    # Initialize language
    language = Language()
    language.set_language(selected_language)

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
