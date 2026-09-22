"""
Экран настроек. Пока заглушка.
Стрелка '←' назад — вернуться на home.
"""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout


class SettingsPage(QWidget):
    back_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(20, 20, 20, 20)

        top = QHBoxLayout()
        self.back_button = QPushButton("←")
        self.back_button.setObjectName("roundButton")
        self.back_button.setCursor(Qt.PointingHandCursor)
        self.back_button.clicked.connect(self.back_requested.emit)
        top.addWidget(self.back_button)
        top.addStretch()

        title = QLabel("settings")
        title.setObjectName("screenTitle")
        title.setAlignment(Qt.AlignCenter)

        root.addLayout(top)
        root.addStretch()
        root.addWidget(title)
        root.addStretch()