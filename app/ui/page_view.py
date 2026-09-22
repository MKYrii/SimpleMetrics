"""
Экран одной страницы метрики.
Сверху: бургер (открыть панель) + стрелка назад.
По центру: заголовок, heatmap, легенда.
"""

from datetime import date

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, QDialog,
    QLineEdit, QCheckBox, QPushButton, QFormLayout, QMessageBox,
)

from app.database import get_page, get_days_for_page, set_day_value
from .colors import legend_colors
from .heatmap_widget import HeatmapWidget


class ValueDialog(QDialog):
    """Модальное окно ввода значения за день."""

    def __init__(self, page, day: date, current_value: float | None, parent=None):
        super().__init__(parent)
        self.setWindowTitle(day.isoformat())
        self.setModal(True)
        self.setMinimumWidth(260)
        self.page = page
        self.day = day
        self.result_value: float | None = None
        self._build_ui(current_value)

    def _build_ui(self, current_value: float | None):
        root = QVBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(12)

        form = QFormLayout()
        form.setSpacing(8)

        if self.page.metric_type == "bool":
            self.checkbox = QCheckBox()
            if current_value is not None:
                self.checkbox.setChecked(current_value >= 1)
            form.addRow("done", self.checkbox)
            self.input = None
        else:
            self.input = QLineEdit()
            if current_value is not None:
                self.input.setText(str(current_value))
            form.addRow("value", self.input)

        root.addLayout(form)

        self.save_button = QPushButton("save")
        self.save_button.setCursor(Qt.PointingHandCursor)
        self.save_button.clicked.connect(self._on_save)
        root.addWidget(self.save_button, alignment=Qt.AlignCenter)

    def _on_save(self):
        if self.page.metric_type == "bool":
            self.result_value = 1.0 if self.checkbox.isChecked() else 0.0
        else:
            text = self.input.text().strip()
            try:
                self.result_value = float(text)
            except ValueError:
                QMessageBox.warning(self, "warning", "value must be a number")
                return
        self.accept()


class PageView(QWidget):
    back_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._page = None
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(20, 16, 20, 20)
        root.setSpacing(16)

        # --- Верхняя панель: бургер + назад ---
        top = QHBoxLayout()
        top.setSpacing(10)
        # Отступ слева 65px: там сидит общий бургер из MainWindow (15px + 40px + 10px зазор)
        top.setContentsMargins(65, 0, 0, 0)

        self.back_button = QPushButton("←")
        self.back_button.setObjectName("roundButton")
        self.back_button.setCursor(Qt.PointingHandCursor)
        self.back_button.clicked.connect(self.back_requested.emit)

        top.addWidget(self.back_button)
        top.addStretch()

        # --- Центрированный контент ---
        content = QVBoxLayout()
        content.setSpacing(16)
        content.setAlignment(Qt.AlignHCenter | Qt.AlignTop)

        self.title_label = QLabel("")
        self.title_label.setObjectName("screenTitle")
        self.title_label.setAlignment(Qt.AlignCenter)

        self.heatmap = HeatmapWidget()
        self.heatmap.day_clicked.connect(self._on_day_clicked)

        self.legend = QWidget()
        self.legend_layout = QHBoxLayout(self.legend)
        self.legend_layout.setContentsMargins(0, 0, 0, 0)
        self.legend_layout.setSpacing(6)

        content.addWidget(self.title_label, alignment=Qt.AlignHCenter)
        content.addWidget(self.heatmap, alignment=Qt.AlignHCenter)
        content.addWidget(self.legend, alignment=Qt.AlignHCenter)

        root.addLayout(top)
        root.addStretch()
        root.addLayout(content)
        root.addStretch()

    def load_page(self, page_id: int):
        self._page = get_page(page_id)
        if self._page is None:
            return

        self.title_label.setText(self._page.name.lower())

        values = get_days_for_page(page_id)
        self.heatmap.set_data(
            values=values,
            min_value=self._page.min_value,
            max_value=self._page.max_value,
            gradient=self._page.gradient,
            gold_threshold=self._page.gold_threshold,
        )
        self._rebuild_legend()

    def _rebuild_legend(self):
        while self.legend_layout.count():
            item = self.legend_layout.takeAt(0)
            w = item.widget()
            if w is not None:
                w.deleteLater()

        colors = legend_colors(self._page.gradient)

        self.legend_layout.addWidget(QLabel("less"))
        for c in colors:
            cell = QLabel()
            cell.setFixedSize(14, 14)
            cell.setStyleSheet(
                f"background-color: {c}; border-radius: 3px;"
            )
            self.legend_layout.addWidget(cell)
        self.legend_layout.addWidget(QLabel("more"))

        if self._page.gold_threshold is not None:
            gold = QLabel()
            gold.setFixedSize(14, 14)
            gold.setStyleSheet("background-color: #FFD700; border-radius: 3px;")
            self.legend_layout.addSpacing(16)
            self.legend_layout.addWidget(gold)
            self.legend_layout.addWidget(
                QLabel(f"gold from {self._page.gold_threshold:g}")
            )

    def _on_day_clicked(self, day: date):
        values = get_days_for_page(self._page.id)
        current = values.get(day)

        dialog = ValueDialog(self._page, day, current, parent=self)
        if dialog.exec() == QDialog.Accepted and dialog.result_value is not None:
            set_day_value(self._page.id, day, dialog.result_value)
            values = get_days_for_page(self._page.id)
            self.heatmap.set_data(
                values=values,
                min_value=self._page.min_value,
                max_value=self._page.max_value,
                gradient=self._page.gradient,
                gold_threshold=self._page.gold_threshold,
            )