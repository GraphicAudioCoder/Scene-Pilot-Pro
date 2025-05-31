from PyQt6.QtWidgets import QFrame, QPushButton, QHBoxLayout, QVBoxLayout, QLabel, QDoubleSpinBox, QSlider, QListWidget, QListWidgetItem, QFileDialog, QLabel, QScrollArea, QPushButton, QVBoxLayout, QHBoxLayout, QWidget, QDialog, QMessageBox, QMenu
from PyQt6.QtGui import QPainter, QPaintEvent, QColor, QFont, QPixmap, QIcon, QGuiApplication, QBrush, QPolygon
from PyQt6.QtCore import QSize, pyqtSignal, Qt, QPoint, QRect
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

        # Initialize the toggle menu
        self.menu_widget = None

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

        dimension_layout = QVBoxLayout()  # Define dimension_layout before usage
        dimension_layout.addWidget(self.width_label)
        dimension_layout.addWidget(self.width_spinbox)
        dimension_layout.addWidget(self.length_label)
        dimension_layout.addWidget(self.length_spinbox)
        dimension_layout.addWidget(self.height_label)
        dimension_layout.addWidget(self.height_spinbox)

        # Add spacing and the "Insert Main Entrance" button
        dimension_layout.addSpacing(10)
        door_button_layout = QHBoxLayout()  # Create a horizontal layout to center the button
        self.insert_door_button = ShapeButton(self, "door")  # Use ShapeButton for the door
        self.insert_door_button.setToolTip(self.language.get("tooltip_insert_main_entrance"))  # Add tooltip
        self.insert_door_button.setFixedSize(50, 50)
        self.insert_door_button.clicked.connect(self.toggle_menu)  # Connect to toggle menu
        door_button_layout.addStretch()  # Add stretch before the button
        door_button_layout.addWidget(self.insert_door_button)
        door_button_layout.addStretch()  # Add stretch after the button
        dimension_layout.addLayout(door_button_layout)  # Add the horizontal layout to the vertical layout
        dimension_layout.addSpacing(10)

        main_layout.addLayout(dimension_layout)  # Add dimension_layout to main_layout

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
        """Display a saved image in the gallery."""
        image_item_widget = QWidget()
        image_item_layout = QVBoxLayout(image_item_widget)  # Use vertical layout for full width
        image_item_layout.setContentsMargins(0, 0, 0, 0)

        # Image preview
        pixmap = QPixmap(image_path).scaled(self.image_gallery_scroll_area.width(), 125, Qt.AspectRatioMode.KeepAspectRatio)
        image_label = ClickableImageLabel(image_path, self)
        image_label.setPixmap(pixmap)
        image_item_layout.addWidget(image_label)

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

    def toggle_menu(self):
        """Toggle the visibility of the menu to the right of the door button."""
        if self.menu_widget and self.menu_widget.isVisible():
            # Nascondi il menu e rimuovi la superficie
            print("Hiding menu")
            self.menu_widget.hide()
            if self.parent_frame:
                self.parent_frame.remove_translucent_wall()  # Rimuove la superficie traslucida
        else:
            if not self.menu_widget:
                self.create_menu()
            self.menu_widget.move(self.insert_door_button.mapToGlobal(QPoint(self.insert_door_button.width() + 10, 0)))
            self.menu_widget.show()
            # Crea la superficie iniziale
            if self.parent_frame:
                self.parent_frame.create_initial_translucent_wall()

    def create_menu(self):
        """Create the menu with left arrow, right arrow, and confirmation buttons."""
        self.menu_widget = QWidget(self)
        self.menu_widget.setWindowFlags(Qt.WindowType.Popup)
        self.menu_widget.setObjectName("menuWidget")  # Assign an object name for QSS styling

        menu_layout = QVBoxLayout(self.menu_widget)
        menu_layout.setContentsMargins(10, 10, 10, 10)
        menu_layout.setSpacing(10)

        # Create the horizontal layout for the arrow and confirmation buttons
        button_layout = QHBoxLayout()

        # Left arrow button
        self.left_arrow_button = QPushButton("←", self.menu_widget)
        self.left_arrow_button.setObjectName("leftArrowButton")
        self.left_arrow_button.setFixedSize(30, 30)
        button_layout.addWidget(self.left_arrow_button)

        # Confirmation button
        self.confirm_button = ShapeButton(self.menu_widget, "hammer")
        self.confirm_button.setObjectName("confirmButton")
        self.confirm_button.setToolTip(self.language.get("tooltip_confirm_selection"))  # Add tooltip
        self.confirm_button.setFixedSize(60, 80)
        button_layout.addWidget(self.confirm_button)

        # Right arrow button
        self.right_arrow_button = QPushButton("→", self.menu_widget)
        self.right_arrow_button.setObjectName("rightArrowButton")
        self.right_arrow_button.setFixedSize(30, 30)
        button_layout.addWidget(self.right_arrow_button)

        menu_layout.addLayout(button_layout)

        # Reduce or remove the vertical spacing below the button layout
        menu_layout.addSpacing(5)  # Reduced from 20 to 5, or remove this line entirely

        # Collegare le frecce alla logica di selezione delle pareti
        self.left_arrow_button.clicked.connect(self.parent_frame.select_previous_wall)
        self.left_arrow_button.clicked.connect(self.validate_door_dimensions)  # Now a class method
        self.right_arrow_button.clicked.connect(self.parent_frame.select_next_wall)
        self.right_arrow_button.clicked.connect(self.validate_door_dimensions)

        # Hide the menu initially
        self.menu_widget.hide()
        self.menu_widget.hideEvent = self.on_menu_hide

        # Add controls for door dimensions and position
        self.door_controls_widget = QWidget(self.menu_widget)
        self.door_controls_widget.setVisible(True)  # Initially hidden
        door_controls_layout = QVBoxLayout(self.door_controls_widget)
        door_controls_layout.setContentsMargins(10, 10, 10, 10)
        door_controls_layout.setSpacing(10)

        # Height control
        height_label = QLabel(self.language.get("label_door_height"), self.door_controls_widget)
        height_spinbox = QDoubleSpinBox(self.door_controls_widget)
        height_spinbox.setRange(0.1, 10.0)
        height_spinbox.setSingleStep(0.1)
        height_spinbox.setSuffix(" m")
        height_spinbox.setValue(2.0)
        door_controls_layout.addWidget(height_label)
        door_controls_layout.addWidget(height_spinbox)

        # Width control
        width_label = QLabel(self.language.get("label_door_width"), self.door_controls_widget)
        width_spinbox = QDoubleSpinBox(self.door_controls_widget)
        width_spinbox.setRange(0.1, 10.0)
        width_spinbox.setSingleStep(0.1)
        width_spinbox.setSuffix(" m")
        width_spinbox.setValue(1.0)
        door_controls_layout.addWidget(width_label)
        door_controls_layout.addWidget(width_spinbox)

        # Position control
        offset_label = QLabel(self.language.get("label_door_offset"), self.door_controls_widget)
        offset_spinbox = QDoubleSpinBox(self.door_controls_widget)
        offset_spinbox.setRange(0.0, 100.0)  # Assuming wall length in meters
        offset_spinbox.setSingleStep(0.1)
        offset_spinbox.setSuffix(" m")
        offset_spinbox.setValue(0.0)
        door_controls_layout.addWidget(offset_label)
        door_controls_layout.addWidget(offset_spinbox)

        # Add validation logic for door dimensions and offset
        width_spinbox.valueChanged.connect(self.validate_door_dimensions)
        offset_spinbox.valueChanged.connect(self.validate_door_dimensions)

        # Add logic to handle door creation validation
        def handle_door_creation():
            total_door_width = width_spinbox.value() + offset_spinbox.value()
            if self.parent_frame and hasattr(self.parent_frame, "get_current_wall_length"):
                wall_length = self.parent_frame.get_current_wall_length()
                if total_door_width > wall_length or height_spinbox.value() > self.height_spinbox.value():
                    QMessageBox.warning(
                        self,
                        self.language.get("error_title"),
                        self.language.get("error_door_exceeds_wall")
                    )
                    return

                reply = QMessageBox.question(
                    self,
                    self.language.get("confirm_new_door_title"),
                    self.language.get("confirm_new_door_message"),
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )

                if reply == QMessageBox.StandardButton.Yes:
                    # Rimuove la porta esistente e crea una nuova
                    if self.parent_frame and hasattr(self.parent_frame, "remove_door_surface"):
                        self.parent_frame.remove_door_surface()

                    # Crea la porta e salvala nel view
                    new_door = self.parent_frame.create_door_surface(
                        width=width_spinbox.value(),
                        height=height_spinbox.value(),
                        offset=offset_spinbox.value()
                    )
                    # Debug: Verifica il valore restituito da create_door_surface
                    # print(f"create_door_surface returned: {new_door}")

                    # Salva la porta nel view per mantenerla
                    if hasattr(self.parent_frame, "view"):
                        self.parent_frame.view.door_mesh = new_door
                        # print(f"Door mesh saved: {new_door}")

        # Connect the toggle button to the door creation logic
        self.confirm_button.clicked.connect(handle_door_creation)

        menu_layout.addWidget(self.door_controls_widget)

        # Add logic to handle room dimension changes
        def handle_room_dimension_change():

            self.parent_frame.view.door_mesh = None

            # Aggiorna le dimensioni della stanza
            self.parent_frame.update_room_plot(
                width=self.width_spinbox.value(),
                length=self.length_spinbox.value(),
                height=self.height_spinbox.value(),
                hue=self.hue_slider.value(),
                saturation=self.saturation_slider.value(),
                value=self.value_slider.value()
            )

        # Connetti le spinbox al gestore delle modifiche
        self.width_spinbox.valueChanged.connect(handle_room_dimension_change)
        self.length_spinbox.valueChanged.connect(handle_room_dimension_change)
        self.height_spinbox.valueChanged.connect(handle_room_dimension_change)

    def on_menu_hide(self, event):
        """Handle the menu hide event to remove the translucent surface and hide door controls."""
        if self.parent_frame:
            self.parent_frame.remove_translucent_wall()
        self.door_controls_widget.setVisible(True)
        event.accept()

    def validate_door_dimensions(self):
        """Validate the door dimensions and adjust if necessary."""
        # if self.door_controls_widget:
        #     width_spinbox = self.door_controls_widget.findChild(QDoubleSpinBox, "widthSpinBox")
        #     offset_spinbox = self.door_controls_widget.findChild(QDoubleSpinBox, "offsetSpinBox")
        #     if width_spinbox and offset_spinbox:
        #         total_door_width = width_spinbox.value() + offset_spinbox.value()
        #         if self.parent_frame and hasattr(self.parent_frame, "get_current_wall_length"):
        #             wall_length = self.parent_frame.get_current_wall_length()
        #             if total_door_width > wall_length:
        #                 width_spinbox.setValue(max(0.1, wall_length - offset_spinbox.value()))
        #                 offset_spinbox.setValue(max(0.0, wall_length - width_spinbox.value()))

class ClickableImageLabel(QLabel):
    def __init__(self, image_path, parent=None):
        super().__init__(parent)
        self.image_path = image_path
        self.parent_frame = parent
        self.setToolTip(self.parent_frame.language.get("tooltip_open_image"))  # Add tooltip

    def contextMenuEvent(self, event):
        """Show a context menu for the image."""
        menu = QMenu(self)
        open_action = menu.addAction(self.parent_frame.language.get("context_menu_open_image"))
        delete_action = menu.addAction(self.parent_frame.language.get("context_menu_delete_image"))

        action = menu.exec(event.globalPos())
        if action == open_action:
            self.parent_frame.show_image_preview(self.image_path)
        elif action == delete_action:
            self.parent_frame.remove_image(self, self.image_path)

    def mousePressEvent(self, ev):
        """Override to disable direct opening on left click."""
        pass

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

        elif self.shape == "door":
            pen = painter.pen()
            pen.setColor(QColor("#FFA500"))  # Orange
            pen.setWidth(1)
            painter.setPen(pen)

            # Fill the door with semi-transparent orange
            painter.setBrush(QColor(255, 165, 0, 50))  # Semi-transparent orange when unselected

            # Draw a filled rectangle representing the door
            painter.drawRect(15, 10, 20, 30)  # Door rectangle

            # Draw the door knob (or handle)
            painter.setBrush(QColor(255, 165, 0, 255))  # Solid orange for the knob
            painter.drawEllipse(28, 25, 4, 4)  # Adjusted position and size for the knob
        elif self.shape == "hammer":
            pen = painter.pen()
            pen.setColor(QColor("#FFA500"))  # Orange
            pen.setWidth(1)
            painter.setPen(pen)

            painter.setBrush(QColor(255, 165, 0, 50))  # Semi-transparent orange

            # Diagonal transformation: rotate painter a bit clockwise around center
            painter.save()
            center = self.rect().center()
            painter.translate(center)
            painter.rotate(20)  # Rotate 20 degrees clockwise
            painter.translate(-center)

            # Hammer handle (vertical rectangle, now diagonal)
            handle_rect = QRect(26, 30, 8, 30)
            painter.drawRect(handle_rect)

            # Draw the hammer outline
            pen.setColor(QColor("#FF8C00"))  # Darker orange for outline
            pen.setWidth(2)
            painter.setPen(pen)
            painter.drawRect(handle_rect)

            # Hammer head (horizontal rectangle, now diagonal)
            painter.setBrush(QColor(255, 165, 0, 120))
            head_rect = QRect(18, 20, 24, 10)
            painter.drawRect(head_rect)

            # Draw the hammer outline
            pen.setColor(QColor("#FF8C00"))  # Darker orange for outline
            pen.setWidth(2)
            painter.setPen(pen)
            painter.drawRect(head_rect)

            painter.restore()
