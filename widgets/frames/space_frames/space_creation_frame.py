from PyQt6.QtWidgets import QFrame, QVBoxLayout, QPushButton, QHBoxLayout, QWidget, QMessageBox
from PyQt6.QtCore import Qt, QEvent, QTimer
from PyQt6.QtGui import QMouseEvent, QVector3D, QPaintEvent, QPainter, QColor  # Import for custom drawing
import pyqtgraph.opengl as gl
from components.space.gizmo import create_axes 
from components.space.room_plot import plot_room, create_translucent_wall, create_door
import numpy as np

class TargetButton(QPushButton):
    """Custom button with a target icon drawn inside."""
    def __init__(self, parent):
        super().__init__(parent)
        self.setFixedSize(60, 60)  # Set the size of the button
        self.color = QColor("#4682B4")  # Default color (steel blue, less bright)

    def set_color(self, color):
        """Set the color of the target icon."""
        self.color = color
        self.update()  # Trigger a repaint

    def paintEvent(self, event: QPaintEvent):
        """Custom paint event to draw the target icon."""
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Draw the outer circle
        pen = painter.pen()
        pen.setColor(self.color)  # Use the dynamic color
        pen.setWidth(2)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawEllipse(12, 12, 36, 36)  # Outer circle, slightly smaller and centered

        # Draw the inner circle
        painter.drawEllipse(18, 18, 24, 24)  # Inner circle (larger and centered)

        # Draw the crosshairs
        # painter.drawLine(30, 5, 30, 55)  # Vertical line, slightly extended
        # painter.drawLine(5, 30, 55, 30)  # Horizontal line, slightly extended
        painter.drawLine(30, 8, 30, 52)  # Vertical line, slightly smaller but centered
        painter.drawLine(8, 30, 52, 30)  # Horizontal line, slightly smaller but centered

class SpaceCreationFrame(QFrame):  # Renamed from CentralFrame
    def __init__(self, language, tool_palette):
        super().__init__()
        self.language = language  # Store the language object
        self.tool_palette = tool_palette  # Store reference to ToolPaletteFrame
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setFrameShape(QFrame.Shape.StyledPanel)

        # Enable mouse events
        self.setAttribute(Qt.WidgetAttribute.WA_AcceptTouchEvents, True)
        self.setMouseTracking(True)

        # 3D layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # 3D view
        self.view = gl.GLViewWidget()
        self.view.setCameraPosition(distance=10, elevation=17, azimuth=295)
        layout.addWidget(self.view)

        # Grid
        grid = gl.GLGridItem()
        grid.setSize(x=10, y=10)
        grid.setSpacing(x=1, y=1)
        self.view.addItem(grid)

        # Axes
        self.gizmo = create_axes(self.view)

        # Event filters
        self.view.installEventFilter(self)
        self.installEventFilter(self)

        # Initial mode
        self.mode = "orbitate"
        self.last_mouse_pos = None

        # Zoom timer
        self.zoom_timer = QTimer()
        self.zoom_timer.setInterval(30)  # Adjust interval for smoothness
        self.zoom_timer.timeout.connect(self.perform_zoom)
        self.zoom_direction = None  # "in" or "out"

        # Timer for smooth zoom
        self.smooth_zoom_timer = QTimer()
        self.smooth_zoom_timer.setInterval(10)  # Short interval for smooth zoom
        self.smooth_zoom_timer.timeout.connect(self.perform_smooth_zoom)
        self.smooth_zoom_direction = None  # "in" or "out"

        # Camera settings
        self.camera_settings = {
            "move": {"distance": 10, "elevation": 90, "azimuth": 270, "center": QVector3D(1.5, 1.5, 0)},
            "orbitate": {"distance": 10, "elevation": 17, "azimuth": 295, "center": QVector3D(0, 0, 0)},
        }

        # Animation time
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self.animate_camera)
        self.animation_steps = 10
        self.current_step = 0
        self.start_camera_settings = {}
        self.target_camera_settings = {}
        self.is_animating = False

        # Overlay container for buttons
        self.overlay_widget = QWidget(self)
        self.overlay_widget.setGeometry(10, 10, 50, 100)  # Position with margin (10px from top and left)

        # Layout for + and - buttons
        overlay_layout = QVBoxLayout(self.overlay_widget)
        overlay_layout.setContentsMargins(0, 0, 0, 0)
        overlay_layout.setSpacing(5)  # Spacing between buttons

        # Add + button
        self.plus_button = QPushButton("+", self.overlay_widget)
        self.plus_button.setFixedSize(40, 40)  # Set button size
        overlay_layout.addWidget(self.plus_button)

        # Add - button
        self.minus_button = QPushButton("-", self.overlay_widget)
        self.minus_button.setFixedSize(40, 40)  # Set button size
        overlay_layout.addWidget(self.minus_button)

        # Add tooltips to the buttons using the language object
        self.plus_button.setToolTip(self.language.get("tooltip_zoom_in"))  # Tooltip for zoom in
        self.minus_button.setToolTip(self.language.get("tooltip_zoom_out"))  # Tooltip for zoom out

        # Connect buttons to zoom actions
        self.plus_button.pressed.connect(lambda: self.start_smooth_zoom("in"))
        self.plus_button.released.connect(self.stop_smooth_zoom)

        self.minus_button.pressed.connect(lambda: self.start_smooth_zoom("out"))
        self.minus_button.released.connect(self.stop_smooth_zoom)

        # Ensure the overlay widget is always on top
        self.overlay_widget.raise_()


        # New container in bottom-left for the empty button
        self.bottom_left_widget = QWidget(self)

        bottom_left_layout = QVBoxLayout(self.bottom_left_widget)
        bottom_left_layout.setContentsMargins(0, 0, 0, 0)
        bottom_left_layout.setSpacing(5)

        # Replace center button with TargetButton
        self.center_button = TargetButton(self.bottom_left_widget)
        self.center_button.setToolTip(self.language.get("tooltip_center_view"))  # Tooltip for centering the view
        self.center_button.clicked.connect(self.center_view)  # Connect to the centering function
        bottom_left_layout.addWidget(self.center_button)

        # size widget to fit its layout (prevent clipping)
        self.bottom_left_widget.setFixedSize(self.bottom_left_widget.sizeHint())
        self.bottom_left_widget.raise_()

        # Room plot reference
        self.room_item = None
        self.axes_items = create_axes(self.view)  # Create axes items for the room plot

        self.room_dimensions = {"width": 3.0, "length": 3.0, "height": 2.0}  # Store room dimensions globally
        self.room_color = {"hue": 216, "saturation": 50, "value": 100}  # Store room color globally

        # Wall selection state
        self.current_wall_index = 0
        self.translucent_wall = None

        # Stato per la gestione della superficie traslucida
        self.translucent_wall_active = False

        # Stato per la gestione della superficie della porta
        self.door_surface = None

    # Calculate camera vectors (right, up).
    def get_camera_vectors(self):
        camera_pos = QVector3D(*self.view.cameraPosition())
        target_pos = self.view.opts['center']
        forward_vector = QVector3D(
            target_pos.x() - camera_pos.x(),
            target_pos.y() - camera_pos.y(),
            target_pos.z() - camera_pos.z()
        )
        forward_vector /= forward_vector.length()

        global_up = QVector3D(0, 0, 1)

        if abs(forward_vector.z()) > 0.99:
            right_vector = QVector3D(1, 0, 0)
            up_vector = QVector3D.crossProduct(right_vector, forward_vector)
        else:
            right_vector = QVector3D.crossProduct(forward_vector, global_up)
            right_vector /= right_vector.length()
            up_vector = QVector3D.crossProduct(right_vector, forward_vector)
            up_vector /= up_vector.length()

        return right_vector, up_vector

    # Zoom in or out.
    def perform_zoom(self):
        if self.zoom_direction == "in":
            self.zoom(0.95)  # Adjust factor for faster/slower zoom in
        elif self.zoom_direction == "out":
            self.zoom(1.05)  # Adjust factor for faster/slower zoom out

    # Perform smooth zoom
    def perform_smooth_zoom(self):
        if self.smooth_zoom_direction == "in":
            self.zoom(0.98)  # Smaller factor for smoother zoom in
        elif self.smooth_zoom_direction == "out":
            self.zoom(1.02)  # Smaller factor for smoother zoom out

    # Start smooth zoom
    def start_smooth_zoom(self, direction):
        self.smooth_zoom_direction = direction
        if not self.smooth_zoom_timer.isActive():
            self.smooth_zoom_timer.start()

    # Stop smooth zoom
    def stop_smooth_zoom(self):
        self.smooth_zoom_timer.stop()
        self.smooth_zoom_direction = None

    # Adjust camera distance.
    def zoom(self, factor):
        current_distance = self.view.opts['distance']
        self.view.setCameraPosition(distance=current_distance * factor)

    # Smooth camera transition.
    def animate_camera(self):
        t = self.current_step / self.animation_steps
        interpolated_settings = {}

        interpolated_settings = {}

        for key in self.start_camera_settings:
            start = self.start_camera_settings[key]
            end = self.target_camera_settings[key]

            if key in ["azimuth", "elevation"]:
                # Normalize angle difference to shortest path
                delta = (end - start + 180) % 360 - 180
                interpolated_value = start + t * delta
            elif key == "center":
                interpolated_value = QVector3D(
                    start.x() + t * (end.x() - start.x()),
                    start.y() + t * (end.y() - start.y()),
                    start.z() + t * (end.z() - start.z()),
                )
            else:
                interpolated_value = start + t * (end - start)

            interpolated_settings[key] = interpolated_value

        self.view.setCameraPosition(
            distance=interpolated_settings["distance"],
            elevation=interpolated_settings["elevation"],
            azimuth=interpolated_settings["azimuth"]
        )
        self.view.opts['center'] = QVector3D(
            interpolated_settings["center"].x(),
            interpolated_settings["center"].y(),
            interpolated_settings["center"].z()
        )
        self.current_step += 1
        if self.current_step > self.animation_steps:
            self.animation_timer.stop()
            self.is_animating = False

    # Switch camera mode.
    def switch_mode(self, mode):
        if self.is_animating:
            return
        self.is_animating = True
        self.mode = mode
        self.start_camera_settings = {
            "distance": self.view.opts['distance'],
            "elevation": self.view.opts['elevation'],
            "azimuth": self.view.opts['azimuth'],
            "center": self.view.opts['center'],
        }
        self.target_camera_settings = self.camera_settings[mode]
        self.current_step = 0
        self.animation_timer.start(30)

    # Save current camera settings.
    def save_camera_settings(self):
        self.camera_settings[self.mode] = {
            "distance": self.view.opts['distance'],
            "elevation": self.view.opts['elevation'],
            "azimuth": self.view.opts['azimuth'],
            "center": self.view.opts['center'],
        }

    # Filter events.
    def eventFilter(self, source, event):
        if self.is_animating:
            if event.type() in (QEvent.Type.Paint, QEvent.Type.UpdateRequest):
                return False
            return True

        if source == self.view and event.type() == QEvent.Type.MouseButtonDblClick:
            if event.button() == Qt.MouseButton.LeftButton:
                # Check the current mode and set the center accordingly
                if self.mode == "move":
                    max_dimension = max(self.room_dimensions["width"], self.room_dimensions["length"], self.room_dimensions["height"])
                    self.view.setCameraPosition(distance=max_dimension * 2)
                    self.view.opts['center'] = QVector3D(self.room_dimensions["width"]/2, self.room_dimensions["length"]/2, 0)
                elif self.mode == "orbitate":
                    max_dimension = max(self.room_dimensions["width"], self.room_dimensions["length"], self.room_dimensions["height"])
                    self.view.setCameraPosition(distance=max_dimension * 2)
                    self.view.opts['center'] = QVector3D(self.room_dimensions["width"]/2, self.room_dimensions["length"]/2, self.room_dimensions["height"]/2)
                event.accept()
                return True

        if event.type() == QEvent.Type.KeyPress:
            key = event.key()
            if key == Qt.Key.Key_P:
                self.save_camera_settings()
                self.switch_mode("move")
            elif key == Qt.Key.Key_O:
                self.save_camera_settings()
                self.switch_mode("orbitate")
            elif key == Qt.Key.Key_Plus:  # Handle '+' key
                self.start_smooth_zoom("in")
                event.accept()
                return True
            elif key == Qt.Key.Key_Minus:  # Handle '-' key
                self.start_smooth_zoom("out")
                event.accept()
                return True

        if event.type() == QEvent.Type.KeyRelease:
            key = event.key()
            if key in (Qt.Key.Key_Plus, Qt.Key.Key_Equal, Qt.Key.Key_Minus):  # Stop zoom on key release
                self.stop_smooth_zoom()
                event.accept()
                return True

        if event.type() == QEvent.Type.MouseMove and self.mode == "move":
            if self.last_mouse_pos is not None:
                delta = event.position() - self.last_mouse_pos
                right_vector, up_vector = self.get_camera_vectors()
                move_x = delta.x() * -0.01
                move_y = delta.y() * 0.01
                move_vector = (
                    right_vector.x() * move_x + up_vector.x() * move_y,
                    right_vector.y() * move_x + up_vector.y() * move_y,
                    right_vector.z() * move_x + up_vector.z() * move_y,
                )
                self.view.pan(move_vector[0], move_vector[1], move_vector[2])

            self.last_mouse_pos = event.position()
            event.accept()
            return True

        if event.type() == QEvent.Type.MouseButtonPress:
            self.last_mouse_pos = event.position()

        if event.type() == QEvent.Type.MouseButtonRelease:
            self.last_mouse_pos = None

        return super().eventFilter(source, event)

    # Zoom in
    def zoom_in(self):
        self.zoom_direction = "in"
        self.perform_zoom()

    # Zoom out
    def zoom_out(self):
        self.zoom_direction = "out"
        self.perform_zoom()

    def update_room_plot(self, width, length, height, hue, saturation, value, door_data=None, render_door=False):
        """Update the room plot with the given dimensions, HSV color, and door data."""
        # Save dimensions and color globally
        self.room_dimensions = {"width": width, "length": length, "height": height}
        self.room_color = {"hue": hue, "saturation": saturation, "value": value}
        self.update_target_button_color()  # Update the target button color
        h = hue / 360.0  # Normalize hue to [0, 1]
        s = saturation / 100.0  # Normalize saturation to [0, 1]
        v = value / 100.0  # Normalize value to [0, 1]
        if render_door:
            self.door_mesh_width = door_data["width"]
            self.door_mesh_height = door_data["height"]
            self.door_mesh_offset = door_data["offset"]
            self.door_mesh_wall_index = door_data["wall_index"]
            new_door = self.create_door_surface(
                self.door_mesh_width, 
                self.door_mesh_height,
                self.door_mesh_offset
            )
            self.view.door_mesh = new_door
        else:
            self.view.door_mesh = None
        # print(door)
        plot_room(self.view, width, length, height, self.axes_items, h=h, s=s, v=v)


    def update_room_color(self, width, length, height, hue, saturation, value, door_data=None):
        """Update the room plot color with the given HSV values and door data."""
        # Save color globally
        self.room_color = {"hue": hue, "saturation": saturation, "value": value}
        self.update_target_button_color()  # Update the target button color
        h = hue / 360.0  # Normalize hue to [0, 1]
        s = saturation / 100.0  # Normalize saturation to [0, 1]
        v = value / 100.0  # Normalize value to [0, 1]

        if self.mode == "move":
            # Preserve the current camera center in move mode
            current_center = self.view.opts['center']
            if self.room_item:
                self.view.removeItem(self.room_item)  # Remove the existing room plot
            plot_room(self.view, width, length, height, self.axes_items, h=h, s=s, v=v, set_center=False, door=False)
            # Restore the camera center
            self.view.opts['center'] = current_center
        else:
            # Default behavior for orbitate mode
            if self.room_item:
                self.view.removeItem(self.room_item)  # Remove the existing room plot
            plot_room(self.view, width, length, height, self.axes_items, h=h, s=s, v=v, door=False)

        # # Render the door if door data is provided
        # if door_data:
        #     create_door(
        #         self.view,
        #         door_data["width"],
        #         door_data["height"],
        #         door_data["offset"],
        #         door_data["wall_index"],
        #         self.room_dimensions,
        #         self.room_color
        #     )

    def update_target_button_color(self):
        """Update the color of the target button based on the current room color."""
        h = self.room_color["hue"] / 360.0
        s = self.room_color["saturation"] / 100.0
        v = self.room_color["value"] / 100.0
        color = QColor.fromHsvF(h, s, v)
        self.center_button.set_color(color)

    def center_view(self):
        """Center the view when the center button is clicked."""
        max_dimension = max(
            self.room_dimensions["width"],
            self.room_dimensions["length"],
            self.room_dimensions["height"]
        )
        # Calcola il centro corretto basandoti sulle dimensioni della stanza
        center_x = self.room_dimensions["width"] / 2
        center_y = self.room_dimensions["length"] / 2
        center_z = self.room_dimensions["height"] / 2

        # Imposta la posizione della telecamera e il centro della vista
        self.view.setCameraPosition(distance=max_dimension * 2)
        self.view.opts['center'] = QVector3D(center_x, center_y, center_z)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        # re-adjust size after any resize
        self.bottom_left_widget.setFixedSize(self.bottom_left_widget.sizeHint())
        margin = 10
        w = self.bottom_left_widget
        w.move(margin, self.height() - w.height() - margin)

    def toggle_wall_selection(self):
        """Toggle the visibility of the translucent wall selection."""
        if self.translucent_wall:
            self.view.removeItem(self.translucent_wall)
            self.translucent_wall = None
        else:
            self.update_translucent_wall()

    def update_translucent_wall(self):
        """Update the translucent wall overlay based on the current wall index."""
        if self.translucent_wall:
            self.view.removeItem(self.translucent_wall)

        room_dims = self.room_dimensions
        room_color = self.room_color
        self.translucent_wall = create_translucent_wall(
            self.view,
            self.current_wall_index,
            room_dims["width"],
            room_dims["length"],
            room_dims["height"],
            h=room_color["hue"] / 360,
            s=room_color["saturation"] / 100,
            v=room_color["value"] / 100,
            alpha=0.3
        )

    def select_next_wall(self):
        """Select the next wall in clockwise order."""
        self.current_wall_index = (self.current_wall_index + 1) % 4
        # print(f"Wall index updated to: {self.current_wall_index}")
        self.update_translucent_wall()

    def select_previous_wall(self):
        """Select the previous wall in counterclockwise order."""
        self.current_wall_index = (self.current_wall_index - 1) % 4
        # print(f"Wall index updated to: {self.current_wall_index}")
        self.update_translucent_wall()

    def hideEvent(self, event):
        """Remove the translucent wall when the frame is hidden."""
        if self.translucent_wall:
            self.view.removeItem(self.translucent_wall)
            self.translucent_wall = None
        super().hideEvent(event)

    def create_initial_translucent_wall(self):
        """Crea la superficie iniziale sopra la prima parete."""
        if not self.translucent_wall_active:
            self.current_wall_index = 0  # Imposta la prima parete
            self.update_translucent_wall()
            self.translucent_wall_active = True

    def remove_translucent_wall(self):
        """Rimuove la superficie traslucida."""
        if self.translucent_wall_active:
            if self.translucent_wall:
                self.view.removeItem(self.translucent_wall)
                self.translucent_wall = None
            self.translucent_wall_active = False

    def create_door_surface(self, width, height, offset):
        """Create a translucent surface to represent the door."""
        # Remove the existing door, if present
        if self.door_surface:
            if self.door_surface in self.view.items:
                self.view.removeItem(self.door_surface)
            self.door_surface = None

        # Use the centralized function to create the door
        self.door_surface = create_door(
            self.view,
            width,
            height,
            offset,
            self.current_wall_index,
            self.room_dimensions,
            self.room_color
        )
        return self.door_surface

    def warn_and_remove_door(self):
        """Mostra un avviso e rimuove la porta se presente."""
        if self.door_surface:
            reply = QMessageBox.warning(
                self,
                self.language.get("warning_title"),
                self.language.get("warning_door_removed"),
                QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel
            )
            if reply == QMessageBox.StandardButton.Ok:
                self.remove_door_surface()
                return True
            return False
        return True

    def get_current_wall_length(self):
        """Restituisce la lunghezza della parete attualmente selezionata."""
        if self.current_wall_index in [0, 2]:  # Pareti 0 e 2 si sviluppano lungo la larghezza
            return self.room_dimensions["width"]
        elif self.current_wall_index in [1, 3]:  # Pareti 1 e 3 si sviluppano lungo la lunghezza
            return self.room_dimensions["length"]
        return 0.0

    def remove_door_surface(self):
        """Rimuove la superficie della porta, se presente."""
        if self.door_surface:
            try:
                self.view.removeItem(self.door_surface)
            except ValueError:
                pass  # Silently handle the case where the door_surface is not in view items
            self.door_surface = None

    def get_door_data(self):
        """Retrieve the current door data if a door is present."""
        if self.door_surface:
            return {
                "width": self.door_surface.width,
                "height": self.door_surface.height,
                "offset": self.door_surface.offset,
                "wall_index": self.door_surface.wall_index
            }
        return None