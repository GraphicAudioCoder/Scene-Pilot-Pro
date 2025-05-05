from PyQt6.QtWidgets import QFrame

class PropertiesFrame(QFrame):
    def __init__(self):
        super().__init__()
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setMinimumWidth(0)
        self.setMaximumWidth(400)
        # Add specific content for the properties frame here
