"""
Экран создания новой страницы.
Форма: name, metric type, gradient, gold threshold, min, max.
По save — пишем в БД и сигналим наружу.
"""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton, QComboBox,
    QVBoxLayout, QHBoxLayout, QFormLayout, QMessageBox,
)

from app.database import create_page


class CreatePage(QWidget):
    back_requested = Signal()
    page_created = Signal(int)  # id новой страницы

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(30, 20, 30, 20)
        root.setSpacing(20)

        # Верх: назад
        # Верх: назад слева, крестик справа
        top = QHBoxLayout()
        self.back_button = QPushButton("←")
        self.back_button.setObjectName("roundButton")
        self.back_button.setCursor(Qt.PointingHandCursor)
        self.back_button.clicked.connect(self.back_requested.emit)
        top.addWidget(self.back_button)
        top.addStretch()

        self.close_button = QPushButton("✕")
        self.close_button.setObjectName("roundButton")
        self.close_button.setCursor(Qt.PointingHandCursor)
        self.close_button.clicked.connect(self.back_requested.emit)
        top.addWidget(self.close_button)

        # Заголовок
        title = QLabel("new page")
        title.setObjectName("screenTitle")
        title.setAlignment(Qt.AlignCenter)

        # Форма
        form = QFormLayout()
        form.setSpacing(12)
        form.setLabelAlignment(Qt.AlignRight)
        form.setFormAlignment(Qt.AlignCenter)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("e.g. reading")

        self.metric_type_input = QComboBox()
        self.metric_type_input.addItems(["bool", "count", "hours"])

        self.gradient_input = QComboBox()
        self.gradient_input.addItems(["red", "green", "blue"])

        self.gold_input = QLineEdit()
        self.gold_input.setPlaceholderText("leave empty to disable")

        self.min_input = QLineEdit("0")
        self.max_input = QLineEdit("10")

        form.addRow("name", self.name_input)
        form.addRow("metric type", self.metric_type_input)
        form.addRow("gradient", self.gradient_input)
        form.addRow("gold threshold", self.gold_input)
        form.addRow("min value", self.min_input)
        form.addRow("max value", self.max_input)

        # Кнопка save
        self.save_button = QPushButton("save")
        self.save_button.setObjectName("createButton")
        self.save_button.setCursor(Qt.PointingHandCursor)
        self.save_button.clicked.connect(self._on_save)

        root.addLayout(top)
        root.addWidget(title)
        root.addStretch()
        root.addLayout(form)
        root.addWidget(self.save_button, alignment=Qt.AlignCenter)
        root.addStretch()

    def _on_save(self):
        name = self.name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "warning", "name cannot be empty")
            return

        try:
            min_v = float(self.min_input.text().strip() or "0")
            max_v = float(self.max_input.text().strip() or "10")
        except ValueError:
            QMessageBox.warning(self, "warning", "min and max must be numbers")
            return

        if max_v <= min_v:
            QMessageBox.warning(self, "warning", "max must be greater than min")
            return

        gold_text = self.gold_input.text().strip()
        gold = None
        if gold_text:
            try:
                gold = float(gold_text)
            except ValueError:
                QMessageBox.warning(self, "warning", "gold threshold must be a number")
                return

        page_id = create_page(
            name=name,
            metric_type=self.metric_type_input.currentText(),
            gradient=self.gradient_input.currentText(),
            gold_threshold=gold,
            min_value=min_v,
            max_value=max_v,
        )
        self._clear_form()
        self.page_created.emit(page_id)

    def _clear_form(self):
        self.name_input.clear()
        self.metric_type_input.setCurrentIndex(0)
        self.gradient_input.setCurrentIndex(0)
        self.gold_input.clear()
        self.min_input.setText("0")
        self.max_input.setText("10")