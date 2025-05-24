import os
import json
from PyQt6.QtWidgets import QFrame, QVBoxLayout, QPushButton, QSpacerItem, QSizePolicy, QLabel, QScrollArea, QWidget, QMessageBox, QLineEdit
from PyQt6.QtGui import QColor
from PyQt6.QtCore import Qt
import pyqtgraph.opengl as gl
from components.space.room_plot import plot_room, create_door  # Import the function to plot the room

class PropertiesFrame(QFrame):
    def __init__(self, space_creation_frame, tool_palette, language, main_window):
        super().__init__()
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setMinimumWidth(0)
        self.setMaximumWidth(600)

        self.space_creation_frame = space_creation_frame
        self.tool_palette = tool_palette
        self.language = language
        self.main_window = main_window  # Reference to MainWindow

        # Layout for the properties frame
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)  # Set margins
        layout.setSpacing(10)

        # Add "New Space" button at the top
        self.new_space_button = QPushButton(self.language.get("button_new_space"))
        self.new_space_button.clicked.connect(self.reset_space)
        layout.addWidget(self.new_space_button)

        # Add a button to refresh the gallery
        self.gallery_button = QPushButton(self.language.get("label_gallery"))
        self.gallery_button.setToolTip(self.language.get("tooltip_refresh_gallery"))
        self.gallery_button.clicked.connect(self.load_saved_spaces)
        layout.addWidget(self.gallery_button)

        # Add search bar above the gallery
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText(self.language.get("placeholder_search_spaces"))
        self.search_bar.textChanged.connect(self.filter_spaces)
        layout.addWidget(self.search_bar)

        # Add a scrollable gallery for saved spaces
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area_widget = QWidget()
        self.scroll_area_layout = QVBoxLayout(self.scroll_area_widget)
        self.scroll_area_layout.setContentsMargins(0, 0, 0, 0)
        self.scroll_area_layout.setSpacing(10)
        self.scroll_area_layout.setAlignment(Qt.AlignmentFlag.AlignTop)  # Align items to the top
        self.scroll_area.setWidget(self.scroll_area_widget)

        # Add the scroll area to the layout and make it expand to fill the remaining space
        layout.addWidget(self.scroll_area, stretch=1)

        # Load saved spaces into the gallery
        self.load_saved_spaces()

    def reset_space(self):
        """Reset the entire CreateSpaceWidget by reloading it."""
        # Show a confirmation dialog
        reply = QMessageBox.question(
            self,
            self.language.get("confirm_new_space_title"),
            self.language.get("confirm_new_space_message"),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.No:
            return

        # Rimuovi CreateSpaceWidget dalla cache del MainWindow utilizzando il nome della classe come chiave
        widget_key = "CreateSpaceWidget"  # Nome della classe come chiave
        if widget_key in self.main_window.widget_cache:
            del self.main_window.widget_cache[widget_key]
        
        # Richiama show_create_space_widget per ricreare il widget
        self.main_window.show_create_space_widget()

    def load_saved_spaces(self):
        """Load saved spaces from the 'spaces' directory and display them in the gallery."""
        self.all_spaces = []  # Store all spaces for filtering
        # Clear the current gallery
        while self.scroll_area_layout.count():
            item = self.scroll_area_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        # Load spaces from the directory
        spaces_dir = "spaces"
        if not os.path.exists(spaces_dir):
            return

        for space_name in os.listdir(spaces_dir):
            space_path = os.path.join(spaces_dir, space_name, f"{space_name}.json")
            if os.path.isfile(space_path):
                with open(space_path, "r") as file:
                    space_data = json.load(file)
                    self.all_spaces.append(space_data)
                    self.add_space_to_gallery(space_data)

    def add_space_to_gallery(self, space_data):
        """Add a space preview to the gallery."""
        # Create a container widget for the space preview
        space_widget = QWidget()
        space_layout = QVBoxLayout(space_widget)
        space_layout.setContentsMargins(10, 10, 10, 10)
        space_layout.setSpacing(5)

        # Add the name of the space as a button
        name_button = QPushButton(space_data.get("name", "Unnamed Space"))
        name_button.setObjectName("new_space_button")  # Use the same object name as new_space_button
        name_button.setToolTip(self.language.get("tooltip_open_model"))  # Add a tooltip
        name_button.clicked.connect(lambda: self.confirm_and_load_model(space_data))  # Connect to confirmation dialog
        space_layout.addWidget(name_button)

        # Create a static OpenGL view for the space
        gl_view = gl.GLViewWidget()
        gl_view.setFixedSize(200, 200)  # Set a fixed size for the preview
        gl_view.setCameraPosition(distance=10, elevation=17, azimuth=295)
        space_layout.addWidget(gl_view)

        # Add a grid to the OpenGL view
        grid = gl.GLGridItem()
        grid.setSize(x=10, y=10)
        grid.setSpacing(x=1, y=1)
        gl_view.addItem(grid)

        # Plot the room in the OpenGL view
        dimensions = space_data.get("coordinates", {})
        color = space_data.get("color", {})
        plot_room(
            gl_view,
            dimensions.get("width", 0),
            dimensions.get("length", 0),
            dimensions.get("height", 0),
            None,  # No axes for the preview
            h=color.get("hue", 0) / 360.0,
            s=color.get("saturation", 0) / 100.0,
            v=color.get("value", 0) / 100.0
        )

        # Plot the door in the OpenGL view if door data is present
        door_data = space_data.get("door", None)
        if door_data:
            create_door(
                gl_view,
                door_data.get("width", 0),
                door_data.get("height", 0),
                door_data.get("offset", 0),
                door_data.get("wall_index", 0),
                dimensions,
                color
            )

        # Add the delete button below the OpenGL view
        delete_button = QPushButton(self.language.get("button_delete"))
        delete_button.setObjectName("delete_space_button")
        delete_button.setToolTip(self.language.get("dialog_delete_message"))
        delete_button.clicked.connect(lambda: self.confirm_and_delete_space(space_data))
        space_layout.addWidget(delete_button)

        # Add the space widget to the gallery
        self.scroll_area_layout.addWidget(space_widget)

    def confirm_and_load_model(self, space_data):
        """Show a confirmation dialog before loading the model."""
        reply = QMessageBox.question(
            self,
            self.language.get("confirm_open_title"),
            self.language.get("confirm_open_message").format(name=space_data.get("name", "Unnamed Space")),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.load_model_to_view(space_data)

    def load_model_to_view(self, space_data):
        """Load the selected model into the SpaceCreationFrame."""
        # Update the SpaceCreationFrame
        dimensions = space_data.get("coordinates", {})
        color = space_data.get("color", {})
        self.space_creation_frame.update_room_plot(
            dimensions.get("width", 0),
            dimensions.get("length", 0),
            dimensions.get("height", 0),
            color.get("hue", 0),
            color.get("saturation", 0),
            color.get("value", 0)
        )

        # Update the ToolPaletteFrame
        self.tool_palette.width_spinbox.setValue(dimensions.get("width", 0))
        self.tool_palette.length_spinbox.setValue(dimensions.get("length", 0))
        self.tool_palette.height_spinbox.setValue(dimensions.get("height", 0))
        self.tool_palette.hue_slider.setValue(color.get("hue", 0))
        self.tool_palette.saturation_slider.setValue(color.get("saturation", 0))
        self.tool_palette.value_slider.setValue(color.get("value", 0))

        # Load saved images into the ToolPaletteFrame
        images_folder = os.path.join("spaces", space_data.get("name", ""), "images")
        if os.path.exists(images_folder):
            images = [os.path.join(images_folder, img) for img in os.listdir(images_folder) if img.endswith(('.png', '.jpg', '.jpeg'))]
            self.tool_palette.load_images(images)

        # Enable the add image button and set the images folder
        self.tool_palette.enable_image_addition(images_folder)

        # Update the SaveSpaceFrame
        save_space_frame = self.main_window.widget_cache["CreateSpaceWidget"].save_space_frame
        save_space_frame.name_input.setText(space_data.get("name", ""))
        save_space_frame.description_input.setText(space_data.get("description", ""))
        save_space_frame.file_path = os.path.join("spaces", space_data.get("name", ""), f"{space_data.get('name', '')}.json")  # Set file path
        save_space_frame.images_folder = images_folder  # Set images folder
        save_space_frame.model_saved = True  # Mark the model as saved

        # Load door data if present
        door_data = space_data.get("door", None)
        print(f"Loading door data: {door_data}")
        if door_data:
            self.space_creation_frame.update_room_plot(
                dimensions.get("width", 0),
                dimensions.get("length", 0),
                dimensions.get("height", 0),
                color.get("hue", 0),
                color.get("saturation", 0),
                color.get("value", 0),
                door_data=door_data,
                render_door=True
            )

    def confirm_and_delete_space(self, space_data):
        """Show a confirmation dialog before deleting the space."""
        reply = QMessageBox.question(
            self,
            self.language.get("dialog_delete_title"),
            self.language.get("dialog_delete_message").format(name=space_data.get("name", "Unnamed Space")),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            # Delete the space directory
            space_name = space_data.get("name", "")
            space_dir = os.path.join("spaces", space_name)
            if os.path.exists(space_dir):
                import shutil
                shutil.rmtree(space_dir)

            # Reload the gallery
            self.load_saved_spaces()

    def filter_spaces(self, text):
        """Filter spaces based on the search text."""
        filtered_spaces = [
            space for space in self.all_spaces if text.lower() in space.get("name", "").lower()
        ]
        # Clear the current gallery
        while self.scroll_area_layout.count():
            item = self.scroll_area_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        # Add filtered spaces to the gallery
        for space in filtered_spaces:
            self.add_space_to_gallery(space)
