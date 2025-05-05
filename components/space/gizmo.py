import numpy as np
from pyqtgraph.opengl import GLLinePlotItem

def create_axes(view):
    axis_length = 0.5
    arrow_length = 0.1
    axes = [
        [(0, 0, 0), (axis_length, 0, 0)],  # X-axis (red)
        [(0, 0, 0), (0, axis_length, 0)],  # Y-axis (green)
        [(0, 0, 0), (0, 0, axis_length)],  # Z-axis (blue)
    ]
    arrow_heads = [
        [(axis_length, 0, 0), (axis_length - arrow_length, 0.05, 0)],
        [(axis_length, 0, 0), (axis_length - arrow_length, -0.05, 0)],
        [(0, axis_length, 0), (0.05, axis_length - arrow_length, 0)],
        [(0, axis_length, 0), (-0.05, axis_length - arrow_length, 0)],
        [(0, 0, axis_length), (0, 0.05, axis_length - arrow_length)],
        [(0, 0, axis_length), (0, -0.05, axis_length - arrow_length)],
    ]
    colors = [(0.8, 0, 0, 1), (0, 0.8, 0, 1), (0, 0, 0.8, 1)]  # Reduced intensity of colors

    axes_items = []
    for i, (start, end) in enumerate(axes):
        pts = np.array([start, end])
        axis_item = GLLinePlotItem(pos=pts, color=colors[i], width=5, antialias=True)  # Increased width to 5
        view.addItem(axis_item)
        axes_items.append(axis_item)

    for i, (start, end) in enumerate(arrow_heads):
        pts = np.array([start, end])
        arrow_item = GLLinePlotItem(pos=pts, color=colors[i // 2], width=5, antialias=True)  # Increased width to 5
        view.addItem(arrow_item)
        axes_items.append(arrow_item)

    return axes_items
