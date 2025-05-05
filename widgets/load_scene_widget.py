from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout

class LoadSceneWidget(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        label = QLabel("Load Scene Widget")
        layout.addWidget(label)
        self.setLayout(layout)
