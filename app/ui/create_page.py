"""
Экран создания новой страницы.
Поля min/max/gold показываются только для числовых типов (count/hours).
Для bool — только name, metric type и gradient.
"""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton, QComboBox,
    QVBoxLayout, QHBoxLayout, QFormLayout, QMessageBox,
)

from app.database import create_page


class CreatePage(QWidget):
    back_requested = Signal()
    page_created = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()
        self._update_numeric_visibility()   # выставить видимость по умолчанию

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(30, 20, 30, 20)
        root.setSpacing(20)

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

        title = QLabel("new page")
        title.setObjectName("screenTitle")
        title.setAlignment(Qt.AlignCenter)

        # --- Форма ---
        form = QFormLayout()
        form.setSpacing(12)
        form.setLabelAlignment(Qt.AlignRight)
        form.setFormAlignment(Qt.AlignCenter)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("e.g. reading")

        self.metric_type_input = QComboBox()
        self.metric_type_input.addItems(["bool", "count", "hours"])
        self.metric_type_input.currentTextChanged.connect(self._update_numeric_visibility)

        self.gradient_input = QComboBox()
        self.gradient_input.addItems(["red", "green", "blue"])

        # Числовые поля — будем скрывать/показывать
        self.min_input = QLineEdit("0")
        self.max_input = QLineEdit("10")
        self.gold_min_input = QLineEdit()
        self.gold_min_input.setPlaceholderText("empty = off")
        self.gold_max_input = QLineEdit()
        self.gold_max_input.setPlaceholderText("empty = off")

        # Лейблы (нужны, чтобы скрывать вместе с полями)
        self.min_label = QLabel("min value")
        self.max_label = QLabel("max value")
        self.gold_min_label = QLabel("gold from")
        self.gold_max_label = QLabel("gold to")

        # Храним пары (label, field) для переключения видимости
        self._numeric_rows = [
            (self.min_label, self.min_input),
            (self.max_label, self.max_input),
            (self.gold_min_label, self.gold_min_input),
            (self.gold_max_label, self.gold_max_input),
        ]

        form.addRow("name", self.name_input)
        form.addRow("metric type", self.metric_type_input)
        form.addRow("gradient", self.gradient_input)
        form.addRow(self.min_label, self.min_input)
        form.addRow(self.max_label, self.max_input)
        form.addRow(self.gold_min_label, self.gold_min_input)
        form.addRow(self.gold_max_label, self.gold_max_input)

        # Сохраняем форму, чтобы потом доставать строки
        self._form = form

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

    def _update_numeric_visibility(self):
        """bool -> скрыть min/max/gold. count/hours -> показать."""
        is_numeric = self.metric_type_input.currentText() != "bool"
        for label, field in self._numeric_rows:
            label.setVisible(is_numeric)
            field.setVisible(is_numeric)

    def _on_save(self):
        name = self.name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "warning", "name cannot be empty")
            return

        metric_type = self.metric_type_input.currentText()

        # Дефолты для bool
        min_v, max_v = 0.0, 1.0
        gold_min = gold_max = None

        if metric_type != "bool":
            try:
                min_v = float(self.min_input.text().strip() or "0")
                max_v = float(self.max_input.text().strip() or "10")
            except ValueError:
                QMessageBox.warning(self, "warning", "min and max must be numbers")
                return

            if max_v <= min_v:
                QMessageBox.warning(self, "warning", "max must be greater than min")
                return

            gmin_text = self.gold_min_input.text().strip()
            gmax_text = self.gold_max_input.text().strip()

            if gmin_text or gmax_text:
                if not (gmin_text and gmax_text):
                    QMessageBox.warning(
                        self, "warning",
                        "fill both gold from and gold to, or leave both empty",
                    )
                    return
                try:
                    gold_min = float(gmin_text)
                    gold_max = float(gmax_text)
                except ValueError:
                    QMessageBox.warning(self, "warning", "gold values must be numbers")
                    return
                if gold_max < gold_min:
                    QMessageBox.warning(self, "warning", "gold to must be >= gold from")
                    return

        page_id = create_page(
            name=name,
            metric_type=metric_type,
            gradient=self.gradient_input.currentText(),
            gold_min=gold_min,
            gold_max=gold_max,
            min_value=min_v,
            max_value=max_v,
        )
        self._clear_form()
        self.page_created.emit(page_id)

    def _clear_form(self):
        self.name_input.clear()
        self.metric_type_input.setCurrentIndex(0)
        self.gradient_input.setCurrentIndex(0)
        self.gold_min_input.clear()
        self.gold_max_input.clear()
        self.min_input.setText("0")
        self.max_input.setText("10")
        self._update_numeric_visibility()