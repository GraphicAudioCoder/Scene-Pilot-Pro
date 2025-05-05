from PyQt6.QtWidgets import QMainWindow, QMenuBar, QWidget, QVBoxLayout
from PyQt6.QtGui import QAction
from PyQt6.QtCore import Qt
from localization.language import Language
from config.constants import PROGRAM_NAME

# Import widgets from their respective files
from widgets.create_scene_widget import CreateSceneWidget
from widgets.load_scene_widget import LoadSceneWidget
from widgets.create_space_widget import CreateSpaceWidget
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
        
        # Connect actions to methods
        create_scene_action.triggered.connect(self.show_create_scene_widget)
        load_scene_action.triggered.connect(self.show_load_scene_widget)
        create_space_action.triggered.connect(self.show_create_space_widget)
        edit_space_action.triggered.connect(self.show_edit_space_widget)
        
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
        if widget_class not in self.widget_cache:
            self.widget_cache[widget_class] = widget_class(*args)
        return self.widget_cache[widget_class]

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
        widget = self.get_or_create_widget(CreateSpaceWidget, self.language)  # Pass the language object
        widget.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.set_central_widget(widget)

    def show_edit_space_widget(self):
        """Show the EditSpaceWidget as the central widget."""
        widget = self.get_or_create_widget(EditSpaceWidget)
        widget.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.set_central_widget(widget)
