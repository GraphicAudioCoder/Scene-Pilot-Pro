from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout

class EditSpaceWidget(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        label = QLabel("Edit Space Widget")
        layout.addWidget(label)
        self.setLayout(layout)
