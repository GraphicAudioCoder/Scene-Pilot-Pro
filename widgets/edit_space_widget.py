from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QScrollArea, QHBoxLayout, QLabel, QPushButton, QFrame, QMessageBox
from PyQt6.QtCore import Qt
import os
import json
import pyqtgraph.opengl as gl
from components.space.room_plot import plot_room
from PyQt6.QtGui import QPixmap
import subprocess

class EditSpaceWidget(QWidget):
    def __init__(self, language, spaces_directory="spaces"):
        super().__init__()
        self.language = language  # Store the language object
        self.spaces_directory = spaces_directory

        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # Search bar
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText(self.language.get("placeholder_search_spaces"))
        self.search_bar.setObjectName("searchBar")  # Use QSS styling
        self.search_bar.textChanged.connect(self.filter_spaces)
        layout.addWidget(self.search_bar)

        # Horizontal gallery
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setObjectName("horizontalGallery")  # Use QSS styling
        self.gallery_widget = QWidget()
        self.gallery_layout = QHBoxLayout(self.gallery_widget)
        self.gallery_layout.setContentsMargins(0, 0, 0, 0)
        self.gallery_layout.setSpacing(20)  # Increase spacing for better layout
        self.scroll_area.setWidget(self.gallery_widget)
        layout.addWidget(self.scroll_area)

        # Load initial spaces
        self.load_spaces()

    def load_spaces(self):
        """Load spaces from the directory."""
        self.spaces = []
        if os.path.exists(self.spaces_directory):
            for space_name in os.listdir(self.spaces_directory):
                space_path = os.path.join(self.spaces_directory, space_name, f"{space_name}.json")
                if os.path.isfile(space_path):
                    with open(space_path, "r") as file:
                        space_data = json.load(file)
                        self.spaces.append(space_data)
        self.display_spaces(self.spaces)

    def filter_spaces(self, text):
        """Filter spaces based on the search text."""
        filtered_spaces = [space for space in self.spaces if text.lower() in space["name"].lower()]
        self.display_spaces(filtered_spaces)

    def display_spaces(self, spaces):
        """Display spaces in the horizontal gallery."""
        # Clear the current gallery
        while self.gallery_layout.count():
            item = self.gallery_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        # Add spaces to the gallery
        for space in spaces:
            space_frame = QFrame()
            space_frame.setObjectName("spaceFrame")  # Use QSS styling
            space_layout = QVBoxLayout(space_frame)
            space_layout.setContentsMargins(10, 10, 10, 10)
            space_layout.setSpacing(10)

            # OpenGL preview
            gl_view = gl.GLViewWidget()
            gl_view.setFixedSize(250, 250)  # Increase size for better layout
            gl_view.setCameraPosition(distance=10, elevation=17, azimuth=295)
            space_layout.addWidget(gl_view)

            # Add a grid to the OpenGL view
            grid = gl.GLGridItem()
            grid.setSize(x=10, y=10)
            grid.setSpacing(x=1, y=1)
            gl_view.addItem(grid)

            # Plot the room in the OpenGL view
            dimensions = space.get("coordinates", {})
            color = space.get("color", {})
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

            # Image gallery below OpenGL
            images_folder = os.path.join("spaces", space["name"], "images")
            image_gallery_layout = QHBoxLayout()
            image_gallery_layout.setContentsMargins(0, 0, 0, 0)
            image_gallery_layout.setSpacing(10)

            # Current image index
            current_image_index = [0]

            # Image display
            image_label = QLabel()
            image_label.setFixedSize(200, 200)
            image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            image_label.setObjectName("imageDisplay")
            image_label.setToolTip(self.language.get("tooltip_open_image"))  # Add tooltip
            image_gallery_layout.addWidget(image_label, alignment=Qt.AlignmentFlag.AlignCenter)

            # Load images
            images = []
            if os.path.exists(images_folder):
                images = [
                    os.path.join(images_folder, img)
                    for img in os.listdir(images_folder)
                    if img.lower().endswith(('.png', '.jpg', '.jpeg'))
                ]
                if images:
                    image_label.setPixmap(QPixmap(images[0]).scaled(200, 200, Qt.AspectRatioMode.KeepAspectRatio))
                    # Connect click event to open image
                    image_label.mousePressEvent = lambda event, img_path=images[0]: self.open_image_with_viewer(img_path)

            # Left arrow button
            left_button = QPushButton("<")
            left_button.setFixedSize(30, 200)  # Match the height of the image
            left_button.clicked.connect(lambda _, idx=current_image_index, imgs=images, lbl=image_label: self.show_previous_image(idx, imgs, lbl))
            image_gallery_layout.insertWidget(0, left_button)  # Insert at the beginning of the layout

            # Right arrow button
            right_button = QPushButton(">")
            right_button.setFixedSize(30, 200)  # Match the height of the image
            right_button.clicked.connect(lambda _, idx=current_image_index, imgs=images, lbl=image_label: self.show_next_image(idx, imgs, lbl))
            image_gallery_layout.addWidget(right_button, alignment=Qt.AlignmentFlag.AlignRight)

            space_layout.addLayout(image_gallery_layout)

            # Space name
            name_label = QLabel(space["name"])
            name_label.setObjectName("spaceNameLabel")  # Use QSS styling
            space_layout.addWidget(name_label, alignment=Qt.AlignmentFlag.AlignCenter)

            # Space description
            description_label = QLabel(space.get("description", self.language.get("label_no_description")))
            description_label.setObjectName("spaceDescriptionLabel")  # Use QSS styling
            description_label.setWordWrap(True)  # Enable word wrapping for long descriptions
            space_layout.addWidget(description_label, alignment=Qt.AlignmentFlag.AlignCenter)

            # Horizontal layout for buttons
            button_layout = QHBoxLayout()
            button_layout.setSpacing(10)

            # Delete button
            delete_button = QPushButton(self.language.get("button_delete"))
            delete_button.setObjectName("deleteButton")  # Use QSS styling
            delete_button.clicked.connect(lambda _, s=space: self.delete_space(s))
            button_layout.addWidget(delete_button)

            space_layout.addLayout(button_layout)
            self.gallery_layout.addWidget(space_frame)

        # Add stretch to align items to the left
        self.gallery_layout.addStretch()

    def view_space(self, space):
        """Handle viewing the selected space."""
        QMessageBox.information(self, self.language.get("dialog_view_title"), self.language.get("dialog_view_message").format(name=space["name"]))

    def delete_space(self, space):
        """Handle deleting the selected space."""
        reply = QMessageBox.question(
            self,
            self.language.get("dialog_delete_title"),
            self.language.get("dialog_delete_message").format(name=space["name"]),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            space_folder = os.path.join(self.spaces_directory, space["name"])
            if os.path.exists(space_folder):
                for root, dirs, files in os.walk(space_folder, topdown=False):
                    for file in files:
                        os.remove(os.path.join(root, file))
                    for dir in dirs:
                        os.rmdir(os.path.join(root, dir))
                os.rmdir(space_folder)
            self.spaces = [s for s in self.spaces if s["name"] != space["name"]]
            self.display_spaces(self.spaces)

    def show_previous_image(self, current_index, images, image_label):
        """Show the previous image in the gallery."""
        if images:
            current_index[0] = (current_index[0] - 1) % len(images)
            image_label.setPixmap(QPixmap(images[current_index[0]]).scaled(200, 200, Qt.AspectRatioMode.KeepAspectRatio))
            # Update click event to open the correct image
            image_label.mousePressEvent = lambda event, img_path=images[current_index[0]]: self.open_image_with_viewer(img_path)

    def show_next_image(self, current_index, images, image_label):
        """Show the next image in the gallery."""
        if images:
            current_index[0] = (current_index[0] + 1) % len(images)
            image_label.setPixmap(QPixmap(images[current_index[0]]).scaled(200, 200, Qt.AspectRatioMode.KeepAspectRatio))
            # Update click event to open the correct image
            image_label.mousePressEvent = lambda event, img_path=images[current_index[0]]: self.open_image_with_viewer(img_path)

    def open_image_with_viewer(self, image_path):
        """Open the image with the system's default image viewer."""
        try:
            subprocess.run(["open", image_path], check=True)  # macOS
        except Exception:
            try:
                subprocess.run(["xdg-open", image_path], check=True)  # Linux
            except Exception:
                try:
                    os.startfile(image_path)  # Windows
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Could not open image: {e}")
