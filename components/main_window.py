import os  # Add this import
import sys  # Add this import
from PyQt6.QtWidgets import QMainWindow, QMenuBar, QWidget, QVBoxLayout, QMessageBox
from PyQt6.QtGui import QAction
from PyQt6.QtCore import Qt
from localization.language import Language
from config.constants import PROGRAM_NAME

# Import widgets from their respective files
from widgets.create_scene_widget import CreateSceneWidget
from widgets.load_scene_widget import LoadSceneWidget
from widgets.edit_space_widget import EditSpaceWidget

class MainWindow(QMainWindow):
    def __init__(self, language):
        super().__init__()
        self.setWindowTitle(PROGRAM_NAME)
        self.showFullScreen()

        self.language = language
        
        # Create menu bar
        menu_bar = self.menuBar()
        
        # Add Scene menu
        scene_menu = menu_bar.addMenu(self.language.get("menu_scene"))
        create_scene_action = QAction(self.language.get("action_create_scene"), self)
        load_scene_action = QAction(self.language.get("action_load_scene"), self)
        scene_menu.addAction(create_scene_action)
        scene_menu.addAction(load_scene_action)
        
        # Add 3D Space menu
        space_menu = menu_bar.addMenu(self.language.get("menu_3d_space"))
        create_space_action = QAction(self.language.get("action_create_space"), self)
        edit_space_action = QAction(self.language.get("action_edit_space"), self)
        space_menu.addAction(create_space_action)
        space_menu.addAction(edit_space_action)
        
        # Add Language menu
        language_menu = menu_bar.addMenu(self.language.get("menu_language"))
        english_action = QAction("English", self)
        italian_action = QAction("Italiano", self)
        language_menu.addAction(english_action)
        language_menu.addAction(italian_action)

        # Connect actions to methods
        create_scene_action.triggered.connect(self.show_create_scene_widget)
        load_scene_action.triggered.connect(self.show_load_scene_widget)
        create_space_action.triggered.connect(self.show_create_space_widget)
        edit_space_action.triggered.connect(self.show_edit_space_widget)
        
        # Connect language actions to methods
        english_action.triggered.connect(lambda: self.confirm_language_switch("en", "English"))
        italian_action.triggered.connect(lambda: self.confirm_language_switch("it", "Italiano"))

        # Set an initial central widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.central_layout = QVBoxLayout(self.central_widget)

        # Cache for widgets
        self.widget_cache = {}

        # Simulate pressing "action_create_space" at startup
        self.show_create_space_widget()

    def set_central_widget(self, widget):
        """Set the central widget dynamically."""
        # Clear the current layout
        for i in reversed(range(self.central_layout.count())):
            item = self.central_layout.itemAt(i)
            widget_to_remove = item.widget()
            if widget_to_remove:
                widget_to_remove.setParent(None)
        
        # Add the new widget
        self.central_layout.addWidget(widget)

    def get_or_create_widget(self, widget_class, *args):
        """Retrieve a cached widget or create a new one if not cached."""
        widget_key = widget_class.__name__  # Use the class name as the key
        if widget_key not in self.widget_cache:
            # Pass the language argument if the widget is EditSpaceWidget
            if widget_class == EditSpaceWidget:
                self.widget_cache[widget_key] = widget_class(self.language, *args)
            else:
                self.widget_cache[widget_key] = widget_class(*args)
        return self.widget_cache[widget_key]

    def show_create_scene_widget(self):
        """Show the CreateSceneWidget as the central widget."""
        widget = self.get_or_create_widget(CreateSceneWidget)
        widget.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.set_central_widget(widget)

    def show_load_scene_widget(self):
        """Show the LoadSceneWidget as the central widget."""
        widget = self.get_or_create_widget(LoadSceneWidget)
        widget.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.set_central_widget(widget)

    def show_create_space_widget(self):
        """Show the CreateSpaceWidget as the central widget."""
        from widgets.create_space_widget import CreateSpaceWidget  # Import here to avoid circular import
        widget = self.get_or_create_widget(CreateSpaceWidget, self.language, self)
        widget.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.set_central_widget(widget)

    def show_edit_space_widget(self):
        """Show the EditSpaceWidget as the central widget."""
        widget = self.get_or_create_widget(EditSpaceWidget)
        widget.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.set_central_widget(widget)

    def confirm_language_switch(self, language_code, language_name):
        """Show a confirmation dialog for switching languages."""
        if self.language.get_current_language() == language_code:  # Use get_current_language method
            QMessageBox.information(
                self,
                self.language.get("info_title"),
                self.language.get("info_already_current_language").format(language=language_name),
            )
            return

        # Get the confirmation message in both the current and target languages
        current_language_message = self.language.get("confirm_language_switch_message")
        target_language_translations = self.language.load_translations(language_code)
        target_language_message = target_language_translations.get("confirm_language_switch_message")

        message = (
            f"{current_language_message}\n\n"
            f"{target_language_message}"
        )
        reply = QMessageBox.question(
            self,
            self.language.get("confirm_title"),
            message,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.switch_language(language_code)

    def switch_language(self, language_code):
        """Switch the application language."""
        self.language.set_language(language_code)
        self.write_language_to_file(language_code)  # Save the language to the file
        self.restart_application(language_code)

    def write_language_to_file(self, language_code):
        """Write the selected language to the file."""
        language_file = os.path.join(os.path.dirname(__file__), "../config/language.txt")
        with open(language_file, "w", encoding="utf-8") as file:
            file.write(language_code)

    def restart_application(self, language_code):
        """Restart the application with the updated language."""
        from PyQt6.QtWidgets import QApplication

        # Ensure the environment variable is set during the restart
        os.environ["OBJC_DISABLE_INITIALIZE_FORK_SAFETY"] = "YES"

        os.execl(
            sys.executable,
            sys.executable,
            *sys.argv,
            f"--language={language_code}"  # Pass the selected language as an argument
        )
        QApplication.quit()

    def retranslate_ui(self):
        """Retranslate the UI elements to the current language."""
        self.menuBar().clear()
        self.__init__(self.language)  # Reinitialize the menu bar with the new language
