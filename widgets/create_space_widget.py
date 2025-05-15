from PyQt6.QtWidgets import QWidget, QVBoxLayout, QSplitter
from PyQt6.QtCore import Qt, QEvent
from PyQt6.QtGui import QShortcut, QKeySequence
from widgets.frames.space_frames.tool_palette_frame import ToolPaletteFrame
from widgets.frames.space_frames.space_creation_frame import SpaceCreationFrame  # Updated import
from widgets.frames.space_frames.properties_frame import PropertiesFrame
from widgets.frames.space_frames.save_space_frame import SaveSpaceFrame

class CreateSpaceWidget(QWidget):
    def __init__(self, language, main_window):
        super().__init__()
        self.language = language
        self.main_window = main_window  # Reference to MainWindow
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.installEventFilter(self)  # Install event filter for key release handling

        # Creazione dello splitter orizzontale principale
        horizontal_splitter = QSplitter(Qt.Orientation.Horizontal)
        horizontal_splitter.setHandleWidth(0)

        # Tool palette a sinistra
        tool_palette = ToolPaletteFrame(language)  # Create ToolPaletteFrame instance
        horizontal_splitter.addWidget(tool_palette)

        # Creazione dello splitter verticale per SpaceCreationFrame e SaveSpaceFrame
        vertical_splitter = QSplitter(Qt.Orientation.Vertical)
        vertical_splitter.setHandleWidth(0)

        # Frame centrale
        central_frame = SpaceCreationFrame(language, tool_palette)  # Pass tool_palette
        vertical_splitter.addWidget(central_frame)

        # Frame per il salvataggio dello spazio
        save_space_frame = SaveSpaceFrame(language, central_frame)  # Pass central_frame
        save_space_frame.setMinimumHeight(0)  # Initially collapsed
        save_space_frame.setMaximumHeight(200)  # Limit maximum height to 200px
        vertical_splitter.addWidget(save_space_frame)
        vertical_splitter.setSizes([600, 200])  # Make the save space frame visible by default
        vertical_splitter.setStretchFactor(0, 4)
        vertical_splitter.setStretchFactor(1, 1)

        # Aggiungi lo splitter verticale al centrale
        horizontal_splitter.addWidget(vertical_splitter)

        # Frame delle proprietà
        right_frame = PropertiesFrame(central_frame, tool_palette, language, main_window)
        right_frame.setMinimumWidth(250)  # Set a smaller minimum width
        right_frame.setMaximumWidth(250)  # Reduce the maximum width
        horizontal_splitter.addWidget(right_frame)

        # Adjust splitter sizes to initially collapse the PropertiesFrame
        horizontal_splitter.setSizes([200, 500, 0])  # Adjust the central frame and properties frame sizes
        horizontal_splitter.setStretchFactor(0, 1)  # Tool palette
        horizontal_splitter.setStretchFactor(1, 4)  # Central frame
        horizontal_splitter.setStretchFactor(2, 0)  # Properties frame starts collapsed

        # Imposta il layout principale
        layout = QVBoxLayout()
        layout.addWidget(horizontal_splitter)
        self.setLayout(layout)

        # Store references for toggling
        self.horizontal_splitter = horizontal_splitter
        self.vertical_splitter = vertical_splitter
        self.save_space_frame = save_space_frame
        self.right_frame = right_frame

        # Collega il segnale dei pulsanti della tool palette alle funzioni dello SpaceCreationFrame
        tool_palette.button_pressed.connect(lambda key: self.handle_tool_palette_action(key, central_frame))

        # Connect spinbox signals to update the room plot
        tool_palette.width_spinbox.valueChanged.connect(lambda value: central_frame.update_room_plot(
            tool_palette.width_spinbox.value(),
            tool_palette.length_spinbox.value(),
            tool_palette.height_spinbox.value(),
            tool_palette.hue_slider.value(),
            tool_palette.saturation_slider.value(),
            tool_palette.value_slider.value()
        ))
        tool_palette.length_spinbox.valueChanged.connect(lambda value: central_frame.update_room_plot(
            tool_palette.width_spinbox.value(),
            tool_palette.length_spinbox.value(),
            tool_palette.height_spinbox.value(),
            tool_palette.hue_slider.value(),
            tool_palette.saturation_slider.value(),
            tool_palette.value_slider.value()
        ))
        tool_palette.height_spinbox.valueChanged.connect(lambda value: central_frame.update_room_plot(
            tool_palette.width_spinbox.value(),
            tool_palette.length_spinbox.value(),
            tool_palette.height_spinbox.value(),
            tool_palette.hue_slider.value(),
            tool_palette.saturation_slider.value(),
            tool_palette.value_slider.value()
        ))

        # Connect HSV sliders to update the room plot color
        tool_palette.hue_slider.valueChanged.connect(lambda value: central_frame.update_room_color(
            tool_palette.width_spinbox.value(),
            tool_palette.length_spinbox.value(),
            tool_palette.height_spinbox.value(),
            tool_palette.hue_slider.value(),
            tool_palette.saturation_slider.value(),
            tool_palette.value_slider.value()
        ))
        tool_palette.saturation_slider.valueChanged.connect(lambda value: central_frame.update_room_color(
            tool_palette.width_spinbox.value(),
            tool_palette.length_spinbox.value(),
            tool_palette.height_spinbox.value(),
            tool_palette.hue_slider.value(),
            tool_palette.saturation_slider.value(),
            tool_palette.value_slider.value()
        ))
        tool_palette.value_slider.valueChanged.connect(lambda value: central_frame.update_room_color(
            tool_palette.width_spinbox.value(),
            tool_palette.length_spinbox.value(),
            tool_palette.height_spinbox.value(),
            tool_palette.hue_slider.value(),
            tool_palette.saturation_slider.value(),
            tool_palette.value_slider.value()
        ))

        # Plot the initial room
        central_frame.update_room_plot(
            tool_palette.width_spinbox.value(),
            tool_palette.length_spinbox.value(),
            tool_palette.height_spinbox.value(),
            tool_palette.hue_slider.value(),
            tool_palette.saturation_slider.value(),
            tool_palette.value_slider.value()
        )

        # Add global shortcuts
        self.add_global_shortcuts(central_frame)

    def add_global_shortcuts(self, central_frame):
        """Add global shortcuts for SpaceCreationFrame and SaveSpaceFrame actions."""
        self.central_frame = central_frame  # Store reference for eventFilter
        shortcut_orbitate = QShortcut(QKeySequence("O"), self)
        shortcut_orbitate.activated.connect(lambda: self.handle_tool_palette_action("O", central_frame))

        shortcut_floor_plan = QShortcut(QKeySequence("P"), self)
        shortcut_floor_plan.activated.connect(lambda: self.handle_tool_palette_action("P", central_frame))

        # Add shortcuts for "+" and "-" for smooth zooming
        shortcut_zoom_in = QShortcut(QKeySequence("+"), self)
        shortcut_zoom_in.activated.connect(lambda: central_frame.start_smooth_zoom("in"))

        shortcut_zoom_out = QShortcut(QKeySequence("-"), self)
        shortcut_zoom_out.activated.connect(lambda: central_frame.start_smooth_zoom("out"))

        # Add shortcut for toggling save space frame
        shortcut_toggle_save_space = QShortcut(QKeySequence("S"), self)
        shortcut_toggle_save_space.activated.connect(self.toggle_save_space_frame)

        # Add shortcut for toggling properties frame
        shortcut_toggle_properties = QShortcut(QKeySequence("R"), self)
        shortcut_toggle_properties.activated.connect(self.toggle_properties_frame)

    def toggle_save_space_frame(self):
        """Toggle the visibility of the save space frame."""
        sizes = self.vertical_splitter.sizes()
        if sizes[1] == 0:  # If the save space frame is collapsed
            self.vertical_splitter.setSizes([600, 200])  # Expand it
        else:
            self.vertical_splitter.setSizes([800, 0])  # Collapse it

    def toggle_properties_frame(self):
        """Toggle the visibility of the properties frame."""
        sizes = self.horizontal_splitter.sizes()
        if sizes[2] == 0:  # If the properties frame is collapsed
            self.horizontal_splitter.setSizes([200, 600, 200])  # Expand it
        else:
            self.horizontal_splitter.setSizes([200, 800, 0])  # Collapse it

    def eventFilter(self, source, event):
        """Handle key release events for stopping smooth zoom."""
        if event.type() == QEvent.Type.KeyPress:
            if event.key() == Qt.Key.Key_Plus:  # "+" key
                self.central_frame.start_smooth_zoom("in")
                return True
            elif event.key() == Qt.Key.Key_Minus:  # "-" key
                self.central_frame.start_smooth_zoom("out")
                return True

        if event.type() == QEvent.Type.KeyRelease:
            if event.key() in (Qt.Key.Key_Plus, Qt.Key.Key_Equal):  # "+" key
                self.central_frame.stop_smooth_zoom()
                return True
            elif event.key() == Qt.Key.Key_Minus:  # "-" key
                self.central_frame.stop_smooth_zoom()
                return True

        return super().eventFilter(source, event)

    def handle_tool_palette_action(self, key, central_frame):
        """Handle actions triggered by the tool palette buttons."""
        tool_palette = self.findChild(ToolPaletteFrame)  # Find the ToolPaletteFrame instance
        if key == "O":
            if central_frame.mode != "orbitate":  # Prevent redundant mode switching
                central_frame.save_camera_settings()
                central_frame.switch_mode("orbitate")
            tool_palette.set_mode("orbitate")  # Synchronize the tool palette with the mode
        elif key == "P":
            if central_frame.mode != "move":  # Prevent redundant mode switching
                central_frame.save_camera_settings()
                central_frame.switch_mode("move")
            tool_palette.set_mode("move")  # Synchronize the tool palette with the mode
