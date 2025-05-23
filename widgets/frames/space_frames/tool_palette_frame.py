from PyQt6.QtWidgets import QFrame, QPushButton, QHBoxLayout, QVBoxLayout, QLabel, QDoubleSpinBox, QSlider, QListWidget, QListWidgetItem, QFileDialog, QLabel, QScrollArea, QPushButton, QVBoxLayout, QHBoxLayout, QWidget, QDialog, QMessageBox
from PyQt6.QtGui import QPainter, QPaintEvent, QColor, QFont, QPixmap, QIcon, QGuiApplication
from PyQt6.QtCore import QSize, pyqtSignal, Qt
import os
import shutil
import subprocess  # Import subprocess for opening files

class ToolPaletteFrame(QFrame):
    button_pressed = pyqtSignal(str)

    def __init__(self, language):
        super().__init__()
        self.language = language
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setMinimumWidth(0)
        self.setMaximumWidth(200)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.setSpacing(0)

        self.cube_button = ShapeButton(self, "cube")
        self.cube_button.setToolTip(self.language.get("tooltip_orbitate"))  # Correct tooltip key
        self.cube_button.clicked.connect(self.select_cube)

        self.square_button = ShapeButton(self, "square")
        self.square_button.setToolTip(self.language.get("tooltip_floor_plan"))  # Correct tooltip key
        self.square_button.clicked.connect(self.select_square)

        button_layout.addWidget(self.cube_button)
        button_layout.addWidget(self.square_button)

        main_layout.addSpacing(10)
        main_layout.addLayout(button_layout)
        main_layout.addSpacing(10)

        label_font = QFont("Poppins", 12)

        self.height_label = QLabel(self.language.get("label_height"))
        self.height_label.setFont(label_font)
        self.height_spinbox = QDoubleSpinBox()
        self.height_spinbox.setRange(0.1, 9999.99)
        self.height_spinbox.setSingleStep(0.1)
        self.height_spinbox.setSuffix(" m")
        self.height_spinbox.setValue(2.0)

        self.length_label = QLabel(self.language.get("label_length"))
        self.length_label.setFont(label_font)
        self.length_spinbox = QDoubleSpinBox()
        self.length_spinbox.setRange(0.1, 9999.99)
        self.length_spinbox.setSingleStep(0.1)
        self.length_spinbox.setSuffix(" m")
        self.length_spinbox.setValue(3.0)

        self.width_label = QLabel(self.language.get("label_width"))
        self.width_label.setFont(label_font)
        self.width_spinbox = QDoubleSpinBox()
        self.width_spinbox.setRange(0.1, 9999.99)
        self.width_spinbox.setSingleStep(0.1)
        self.width_spinbox.setSuffix(" m")
        self.width_spinbox.setValue(3.0)

        dimension_layout = QVBoxLayout()
        dimension_layout.addWidget(self.width_label)
        dimension_layout.addWidget(self.width_spinbox)
        dimension_layout.addWidget(self.length_label)
        dimension_layout.addWidget(self.length_spinbox)
        dimension_layout.addWidget(self.height_label)
        dimension_layout.addWidget(self.height_spinbox)

        main_layout.addLayout(dimension_layout)

        # Add HSV sliders and labels
        hsv_layout = QVBoxLayout()

        self.hue_label = QLabel(self.language.get("label_hue"))
        self.hue_label.setFont(label_font)
        self.hue_slider = QSlider(Qt.Orientation.Horizontal)
        self.hue_slider.setRange(0, 360)  # Hue range in degrees
        self.hue_slider.setValue(216)  # Default value (0.6 * 360)
        self.hue_slider.valueChanged.connect(self.update_slider_colors)  # Update colors dynamically
        hsv_layout.addWidget(self.hue_label)
        hsv_layout.addWidget(self.hue_slider)

        self.saturation_label = QLabel(self.language.get("label_saturation"))
        self.saturation_label.setFont(label_font)
        self.saturation_slider = QSlider(Qt.Orientation.Horizontal)
        self.saturation_slider.setRange(0, 100)  # Saturation range as percentage
        self.saturation_slider.setValue(50)  # Default value (0.5 * 100)
        self.saturation_slider.valueChanged.connect(self.update_slider_colors)
        hsv_layout.addWidget(self.saturation_label)
        hsv_layout.addWidget(self.saturation_slider)

        self.value_label = QLabel(self.language.get("label_value"))
        self.value_label.setFont(label_font)
        self.value_slider = QSlider(Qt.Orientation.Horizontal)
        self.value_slider.setRange(0, 100)  # Value range as percentage
        self.value_slider.setValue(100)  # Default value (1.0 * 100)
        self.value_slider.valueChanged.connect(self.update_slider_colors)
        hsv_layout.addWidget(self.value_label)
        hsv_layout.addWidget(self.value_slider)

        main_layout.addLayout(hsv_layout)  # Add HSV layout to the main layout

        # Remove the extra stretch to ensure the image gallery starts immediately below
        # main_layout.addStretch()  # Push everything else to the bottom

        # Image gallery section
        self.image_gallery_label = QLabel(self.language.get("label_image_gallery"))
        self.image_gallery_scroll_area = QScrollArea()
        self.image_gallery_scroll_area.setWidgetResizable(True)
        self.image_gallery_widget = QWidget()
        self.image_gallery_layout = QVBoxLayout(self.image_gallery_widget)
        self.image_gallery_scroll_area.setWidget(self.image_gallery_widget)

        self.add_image_button = QPushButton(self.language.get("button_add_image"))
        self.add_image_button.clicked.connect(self.add_image)
        self.add_image_button.setEnabled(False)  # Disable the button initially
        self.add_image_button.setStyleSheet("""
            QPushButton:disabled {
                background-color: #243447; /* Slightly lighter blue for disabled state */
                color: #666666; /* Gray text for disabled state */
                border: 1px solid #415a77; /* Keep the border consistent */
            }
        """)

        gallery_layout = QVBoxLayout()
        gallery_layout.addWidget(self.image_gallery_label)
        gallery_layout.addWidget(self.image_gallery_scroll_area)
        gallery_layout.addWidget(self.add_image_button)
        main_layout.addLayout(gallery_layout)

        self.images = []  # Store image paths
        self.model_saved = False  # Track if the model has been saved
        self.images_folder = None  # Folder to save images after model is saved
        self.add_image_button.setEnabled(False)  # Disable the button initially

        # Set default mode and update slider colors
        self.select_cube()  # Select "Orbitate" mode by default
        self.update_slider_colors()  # Update slider handle colors based on default HSV values

    def enable_image_addition(self, images_folder):
        """Enable the 'Add Image' button and set the folder for saving images."""
        self.model_saved = True
        self.images_folder = images_folder  # Set the images folder
        self.add_image_button.setEnabled(True)

    def select_cube(self):
        """Select the cube (orbitate) mode."""
        self.cube_button.setSelected(True)
        self.square_button.setSelected(False)
        self.button_pressed.emit("O")  # Emit signal for orbitate mode

    def select_square(self):
        """Select the square (move) mode."""
        self.cube_button.setSelected(False)
        self.square_button.setSelected(True)
        self.button_pressed.emit("P")  # Emit signal for move mode

    def set_mode(self, mode):
        """Set the current mode and update button styles."""
        if mode == "orbitate":
            self.cube_button.setSelected(True)
            self.square_button.setSelected(False)
        elif mode == "move":
            self.cube_button.setSelected(False)
            self.square_button.setSelected(True)

    def update_slider_colors(self):
        """Update the slider handle colors based on the current HSV values."""
        hue = self.hue_slider.value()
        saturation = self.saturation_slider.value() / 100.0
        value = self.value_slider.value() / 100.0
        color = QColor.fromHsvF(hue / 360.0, saturation, value)
        rgb = color.name()  # Get the RGB hex value

        # Update the handle colors for each slider
        self.hue_slider.setStyleSheet(f"QSlider::handle:horizontal {{ background: {rgb}; }}")
        self.saturation_slider.setStyleSheet(f"QSlider::handle:horizontal {{ background: {rgb}; }}")
        self.value_slider.setStyleSheet(f"QSlider::handle:horizontal {{ background: {rgb}; }}")

    def add_image(self):
        """Open a file dialog to add an image and save it directly."""
        if not self.model_saved:
            QMessageBox.warning(self, self.language.get("error_title"), self.language.get("error_save_model_first"))
            return

        image_path, _ = QFileDialog.getOpenFileName(self, self.language.get("dialog_select_image"), "", "Images (*.png *.jpg *.jpeg)")
        if image_path:
            # Ensure the images folder exists
            if self.images_folder is not None and not os.path.exists(self.images_folder):
                os.makedirs(self.images_folder, exist_ok=True)

            # Generate a unique name for the image
            original_name = os.path.basename(image_path)
            name, ext = os.path.splitext(original_name)
            counter = 1
            new_name = original_name
            images_folder_str = str(self.images_folder)
            while os.path.exists(os.path.join(images_folder_str, new_name)):
                new_name = f"{name}_{counter}{ext}"
                counter += 1

            saved_image_path = os.path.join(str(self.images_folder), new_name)
            shutil.copy(image_path, saved_image_path)  # Save the image without compression
            self.images.append(saved_image_path)  # Store the saved image path
            self.display_image(saved_image_path)

    def display_image(self, image_path):
        """Display a saved image in the gallery with a remove button."""
        image_item_widget = QWidget()
        image_item_layout = QHBoxLayout(image_item_widget)
        image_item_layout.setContentsMargins(0, 0, 0, 0)

        # Image preview
        pixmap = QPixmap(image_path).scaled(125, 125, Qt.AspectRatioMode.KeepAspectRatio)
        image_label = ClickableImageLabel(image_path, self)
        image_label.setPixmap(pixmap)
        image_item_layout.addWidget(image_label)

        # Remove button
        remove_button = QPushButton("X")
        remove_button.setFixedSize(20, 20)  # Smaller size
        remove_button.setStyleSheet("""
            QPushButton {
                color: #AA0000; /* Dark red */
                font-weight: bold;
                border: none;
                background: transparent;
            }
            QPushButton:hover {
                color: #FF0000; /* Brighter red on hover */
            }
        """)
        remove_button.clicked.connect(lambda: self.remove_image(image_item_widget, image_path))
        image_item_layout.addWidget(remove_button)

        self.image_gallery_layout.addWidget(image_item_widget)

    def show_image_preview(self, image_path):
        """Open the saved image using the default image viewer."""
        if not self.model_saved:
            QMessageBox.warning(self, self.language.get("error_title"), self.language.get("error_save_model_first"))
            return

        # Ensure the image path is from the saved images folder
        if not image_path.startswith(self.images_folder):
            QMessageBox.warning(self, self.language.get("error_title"), self.language.get("error_invalid_image_path"))
            return

        try:
            # Open the image with the default image viewer
            subprocess.run(["open", image_path], check=True)  # macOS-specific command
        except Exception as e:
            QMessageBox.critical(
                self,
                self.language.get("error_title"),
                self.language.get("error_opening_image").format(error=str(e))
            )

    def remove_image(self, image_item_widget, image_path):
        """Remove an image from the gallery and delete it from the saved folder."""
        reply = QMessageBox.question(
            self,
            self.language.get("dialog_delete_image_title"),
            self.language.get("dialog_delete_image_message"),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.image_gallery_layout.removeWidget(image_item_widget)
            image_item_widget.deleteLater()
            self.images.remove(image_path)
            if os.path.exists(image_path):
                os.remove(image_path)  # Delete the saved image file

    def load_images(self, images):
        """Load saved images into the tool palette."""
        self.images = images
        self.clear_image_gallery()  # Clear the gallery before adding new images
        for image_path in images:
            self.display_image(image_path)  # Display each image in the gallery

    def clear_image_gallery(self):
        """Clear the image gallery in the tool palette."""
        while self.image_gallery_layout.count():
            item = self.image_gallery_layout.takeAt(0)
            if item is not None:
                widget = item.widget()
                if widget:
                    widget.deleteLater()

class ClickableImageLabel(QLabel):
    def __init__(self, image_path, parent=None):
        super().__init__(parent)
        self.image_path = image_path
        self.parent_frame = parent
        self.setToolTip(self.parent_frame.language.get("tooltip_open_image"))  # Add tooltip

    def mousePressEvent(self, ev):
        if self.parent_frame is not None and hasattr(self.parent_frame, "show_image_preview"):
            self.parent_frame.show_image_preview(self.image_path)

class ShapeButton(QPushButton):
    def __init__(self, parent, shape):
        super().__init__(parent)
        self.shape = shape
        self.setFixedSize(QSize(50, 50))
        self.selected = False
    def setSelected(self, selected: bool):
        self.selected = selected
        self.update()

    def paintEvent(self, a0: QPaintEvent | None):
        super().paintEvent(a0)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        if self.shape == "cube":
            pen = painter.pen()
            pen.setColor(QColor("#00FFFF"))  # Bright cyan
            pen.setWidth(1)
            painter.setPen(pen)

            if self.selected:
                painter.setBrush(QColor(0, 255, 255, 100))  # Cyan with transparency
            else:
                painter.setBrush(Qt.BrushStyle.NoBrush)

            # Front face
            painter.drawRect(10, 14, 26, 26)

            painter.setBrush(Qt.BrushStyle.NoBrush)  # Disable brush for other faces
            # Top face
            painter.drawRect(16, 8, 26, 26)
            # Connecting lines
            painter.drawLine(10, 14, 16, 8)
            painter.drawLine(36, 14, 42, 8)
            painter.drawLine(36, 40, 42, 34)
            painter.drawLine(10, 40, 16, 34)

        elif self.shape == "square":
            pen = painter.pen()
            pen.setColor(QColor("#FF00FF"))  # Bright magenta
            pen.setWidth(1)
            painter.setPen(pen)

            if self.selected:
                painter.setBrush(QColor(255, 0, 255, 100))  # Magenta with transparency
            else:
                painter.setBrush(Qt.BrushStyle.NoBrush)

            painter.drawRect(10, 10, 30, 30)
