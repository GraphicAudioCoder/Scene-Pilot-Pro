from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout

class CreateSceneWidget(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        label = QLabel("Create Scene Widget")
        layout.addWidget(label)
        self.setLayout(layout)
