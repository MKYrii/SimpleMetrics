"""
Экран 'hello' — главная страница.
Только центрированные hello и create.
Список страниц теперь в MainWindow (выезжающая панель).
"""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QWidget, QLabel, QPushButton, QVBoxLayout


class HomePage(QWidget):
    create_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(30)
        root.setAlignment(Qt.AlignCenter)

        self.hello_label = QLabel("hello")
        self.hello_label.setObjectName("helloLabel")
        self.hello_label.setAlignment(Qt.AlignCenter)

        self.create_button = QPushButton("create")
        self.create_button.setObjectName("createButton")
        self.create_button.setCursor(Qt.PointingHandCursor)
        self.create_button.clicked.connect(self.create_requested.emit)

        root.addWidget(self.hello_label, alignment=Qt.AlignCenter)
        root.addWidget(self.create_button, alignment=Qt.AlignCenter)