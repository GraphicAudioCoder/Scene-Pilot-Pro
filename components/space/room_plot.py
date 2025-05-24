import numpy as np
import pyqtgraph.opengl as gl
import pyqtgraph as pg
from PyQt6.QtGui import QColor

def plot_room(view, Lx, Ly, Lz, axes_items, h=0.6, s=0.5, v=1.0, set_center=True, door=True):
    view.clear()

    edges = [
        [(0, 0, 0), (Lx, 0, 0)],
        [(Lx, 0, 0), (Lx, Ly, 0)],
        [(Lx, Ly, 0), (0, Ly, 0)],

        [(0, Ly, 0), (0, 0, 0)],
        [(0, 0, Lz), (Lx, 0, Lz)],
        [(Lx, 0, Lz), (Lx, Ly, Lz)],

        [(Lx, Ly, Lz), (0, Ly, Lz)],
        [(0, Ly, Lz), (0, 0, Lz)],
        [(0, 0, 0), (0, 0, Lz)],
        
        [(Lx, 0, 0), (Lx, 0, Lz)],
        [(Lx, Ly, 0), (Lx, Ly, Lz)],
        [(0, Ly, 0), (0, Ly, Lz)],
    ]

    color = QColor.fromHsvF(h, s, v)
    r, g, b, a = color.redF(), color.greenF(), color.blueF(), color.alphaF()

    # Draw edges
    for start, end in edges:
        pts = np.array([start, end])
        plt = gl.GLLinePlotItem(pos=pts, color=(r, g, b, a), width=3, antialias=True)  # Increased width to 3
        view.addItem(plt)

    # Draw base area
    base_color = QColor.fromHsvF(h, s, v, alpha=0.3)  # Semi-transparent base
    r_base, g_base, b_base, a_base = base_color.redF(), base_color.greenF(), base_color.blueF(), base_color.alphaF()
    vertices = np.array([
        [0, 0, 0],
        [Lx, 0, 0],
        [Lx, Ly, 0],
        [0, Ly, 0]
    ])
    faces = np.array([
        [0, 1, 2],
        [0, 2, 3]
    ])
    base_mesh = gl.GLMeshItem(vertexes=vertices, faces=faces, faceColors=[(r_base, g_base, b_base, a_base)] * 2, smooth=False)
    base_mesh.setGLOptions('additive')  # Enable blending and disable depth testing
    view.addItem(base_mesh)

    # Draw grid
    grid = gl.GLGridItem()
    grid.setSize(x=Lx, y=Ly)
    grid.setSpacing(x=1, y=1)
    grid.translate(Lx / 2, Ly / 2, 0)
    view.addItem(grid)

    # Set center if required
    if set_center:
        center = np.array([Lx / 2, Ly / 2, Lz / 2])
        view.opts['center'] = pg.Vector(center[0], center[1], center[2])

    # Add axes
    if axes_items:  # Check if axes_items is not None
        for axis_item in axes_items:
            view.addItem(axis_item)

    # Recreate the door if it exists
    if hasattr(view, 'door_mesh') and view.door_mesh is not None:
        view.door_mesh = create_door(
            view,
            view.door_mesh.width,  # Assuming width is stored in the door_mesh
            view.door_mesh.height,  # Assuming height is stored in the door_mesh
            view.door_mesh.offset,  # Assuming offset is stored in the door_mesh
            view.door_mesh.wall_index,  # Assuming wall_index is stored in the door_mesh
            {'width': Lx, 'length': Ly, 'height': Lz},
            {'hue': h * 360, 'saturation': s * 100, 'value': v * 100}
        )

def create_translucent_wall(view, wall_index, Lx, Ly, Lz, h=0.6, s=0.5, v=1.0, alpha=0.3):
    """
    Create a translucent wall overlay on a specific wall of the room.

    Parameters:
        view: The GLViewWidget to add the wall to.
        wall_index: The index of the wall (0 to 3 for the base walls).
        Lx, Ly, Lz: Dimensions of the room.
        h, s, v: HSV color values for the wall.
        alpha: Transparency of the wall.
    """
    walls = [
        [(0, 0, 0), (Lx, 0, 0), (Lx, 0, Lz), (0, 0, Lz)],  # Wall 0
        [(Lx, 0, 0), (Lx, Ly, 0), (Lx, Ly, Lz), (Lx, 0, Lz)],  # Wall 1
        [(Lx, Ly, 0), (0, Ly, 0), (0, Ly, Lz), (Lx, Ly, Lz)],  # Wall 2
        [(0, Ly, 0), (0, 0, 0), (0, 0, Lz), (0, Ly, Lz)],  # Wall 3
    ]

    if wall_index < 0 or wall_index >= len(walls):
        raise ValueError("Invalid wall index")

    vertices = np.array(walls[wall_index])
    faces = np.array([
        [0, 1, 2],
        [0, 2, 3]
    ])

    color = QColor.fromHsvF(h, s, v, alpha)
    r, g, b, a = color.redF(), color.greenF(), color.blueF(), color.alphaF()

    wall_mesh = gl.GLMeshItem(vertexes=vertices, faces=faces, faceColors=[(r, g, b, a)] * 2, smooth=False)
    wall_mesh.setGLOptions('additive')  # Enable blending and disable depth testing
    view.addItem(wall_mesh)

    return wall_mesh

def create_door(view, width, height, offset, wall_index, room_dims, room_color):
    """
    Create a translucent surface to represent the door.

    Parameters:
        view: The GLViewWidget to add the door to.
        width: The width of the door.
        height: The height of the door.
        offset: The offset of the door from the wall's edge.
        wall_index: The index of the wall where the door is placed.
        room_dims: Dictionary containing room dimensions (width, length, height).
        room_color: Dictionary containing room color (hue, saturation, value).

    Returns:
        The created door surface (GLMeshItem).
    """
    # Calculate door vertices based on the selected wall
    if wall_index == 0:  # Front wall (width)
        vertices = [
            (offset, 0, 0),
            (offset + width, 0, 0),
            (offset + width, 0, height),
            (offset, 0, height)
        ]
    elif wall_index == 1:  # Right wall (length)
        vertices = [
            (room_dims["width"], offset, 0),
            (room_dims["width"], offset + width, 0),
            (room_dims["width"], offset + width, height),
            (room_dims["width"], offset, height)
        ]
    elif wall_index == 2:  # Bottom wall (width)
        vertices = [
            (room_dims["width"] - offset, room_dims["length"], 0),
            (room_dims["width"] - offset - width, room_dims["length"], 0),
            (room_dims["width"] - offset - width, room_dims["length"], height),
            (room_dims["width"] - offset, room_dims["length"], height)
        ]
    elif wall_index == 3:  # Left wall (length)
        vertices = [
            (0, room_dims["length"] - offset, 0),
            (0, room_dims["length"] - offset - width, 0),
            (0, room_dims["length"] - offset - width, height),
            (0, room_dims["length"] - offset, height)
        ]
    else:
        return None

    # Calculate door color based on room color
    h = room_color["hue"] / 360.0
    s = room_color["saturation"] / 100.0
    v = room_color["value"] / 100.0
    color = QColor.fromHsvF(h, s, v, 0.5)  # 50% transparency
    r, g, b, a = color.redF(), color.greenF(), color.blueF(), color.alphaF()

    # Create the door surface
    door_surface = gl.GLMeshItem(
        vertexes=np.array(vertices),
        faces=np.array([[0, 1, 2], [0, 2, 3]]),
        faceColors=[(r, g, b, a)] * 2,  # Color based on the room
        smooth=False
    )
    door_surface.setGLOptions('additive')  # Enable blending
    view.addItem(door_surface)

    # Add custom attributes to the door surface for later use
    door_surface.width = width
    door_surface.height = height
    door_surface.offset = offset
    door_surface.wall_index = wall_index

    return door_surface
