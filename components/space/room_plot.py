import numpy as np
import pyqtgraph.opengl as gl
import pyqtgraph as pg
from PyQt6.QtGui import QColor

def plot_room(view, Lx, Ly, Lz, axes_items, h=0.6, s=0.5, v=1.0, set_center=True):
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
