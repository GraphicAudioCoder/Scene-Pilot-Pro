from PyQt6.QtWidgets import QFrame, QVBoxLayout, QLabel, QLineEdit, QTextEdit, QPushButton, QMessageBox
import os
import json
import shutil  # Import shutil for copying files

class SaveSpaceFrame(QFrame):
    def __init__(self, language, space_creation_frame):
        super().__init__()
        self.language = language
        self.space_creation_frame = space_creation_frame  # Reference to SpaceCreationFrame
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setMinimumHeight(0)  # Initially collapsed
        self.setMaximumHeight(200)  # Limit maximum height to 200px

        # Layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(5)

        # Name input
        self.name_label = QLabel(self.language.get("label_name"))
        self.name_input = QLineEdit()
        layout.addWidget(self.name_label)
        layout.addWidget(self.name_input)

        # Description input
        self.description_label = QLabel(self.language.get("label_description"))
        self.description_input = QTextEdit()
        layout.addWidget(self.description_label)
        layout.addWidget(self.description_input)

        # Save button
        self.save_button = QPushButton(self.language.get("button_save"))
        self.save_button.clicked.connect(self.save_model)
        layout.addWidget(self.save_button)

    def save_model(self):
        """Save the model's properties to a file."""
        name = self.name_input.text().strip()
        description = self.description_input.toPlainText().strip()

        if not name:
            QMessageBox.warning(self, self.language.get("error_title"), self.language.get("error_name_required"))
            return

        # Retrieve actual dimensions and color from SpaceCreationFrame
        dimensions = {
            "width": round(self.space_creation_frame.room_dimensions["width"], 2),
            "length": round(self.space_creation_frame.room_dimensions["length"], 2),
            "height": round(self.space_creation_frame.room_dimensions["height"], 2)
        }
        color = {
            "hue": round(self.space_creation_frame.room_color["hue"], 0),
            "saturation": round(self.space_creation_frame.room_color["saturation"], 0),
            "value": round(self.space_creation_frame.room_color["value"], 0)
        }

        model_data = {
            "name": name,
            "description": description,
            "coordinates": dimensions,  # Use rounded dimensions
            "color": color  # Use rounded color values
        }

        # Retrieve door data if present
        door_data = None
        if self.space_creation_frame.view.door_mesh:
            door_data = {
                "width": round(self.space_creation_frame.view.door_mesh.width, 2),
                "height": round(self.space_creation_frame.view.door_mesh.height, 2),
                "offset": round(self.space_creation_frame.view.door_mesh.offset, 2),
                "wall_index": self.space_creation_frame.view.door_mesh.wall_index
            }

        # Add door data to model_data if present
        if door_data:
            model_data["door"] = door_data

        # Create a subfolder for the space
        space_folder = os.path.join("spaces", name)
        images_folder = os.path.join(space_folder, "images")
        os.makedirs(space_folder, exist_ok=True)
        file_path = os.path.join(space_folder, f"{name}.json")

        # Check if the file already exists
        if os.path.exists(file_path):
            reply = QMessageBox.question(
                self,
                self.language.get("overwrite_title"),
                self.language.get("overwrite_message").format(name=name),
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.No:
                return

            # Delete the existing images folder only if the tool palette has no images
            if not self.space_creation_frame.tool_palette.images and os.path.exists(images_folder):
                shutil.rmtree(images_folder)

        # Write the JSON file
        try:
            with open(file_path, "w") as file:
                json.dump(model_data, file, indent=4)
        except Exception as e:
            QMessageBox.critical(
                self,
                self.language.get("error_title"),
                self.language.get("error_saving_file").format(error=str(e))
            )
            return

        # Enable image addition in ToolPaletteFrame
        self.space_creation_frame.tool_palette.enable_image_addition(images_folder)

        # Do not modify the images folder if the tool palette contains images
        if not self.space_creation_frame.tool_palette.images:
            os.makedirs(images_folder, exist_ok=True)

        # Notify the PropertiesFrame to reload the gallery
        if hasattr(self.space_creation_frame, 'properties_frame'):
            self.space_creation_frame.properties_frame.load_saved_spaces()

        QMessageBox.information(self, self.language.get("success_title"), self.language.get("success_message"))
