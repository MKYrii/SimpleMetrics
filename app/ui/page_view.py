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

from app.database import get_page, get_days_for_page, set_day_value, delete_page
from .colors import legend_colors
from .heatmap_widget import HeatmapWidget
from .edit_page_dialog import EditPageDialog


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
        root.setContentsMargins(20, 10, 20, 20)
        root.setSpacing(12)

        if self.page.metric_type == "bool":
            already_done = current_value is not None and current_value >= 1
            label = "not done" if already_done else "done"
            self.checkbox = QCheckBox(label)
            self.checkbox.setObjectName("boolToggle")
            self.checkbox.setChecked(already_done)
            self.checkbox.toggled.connect(self._on_bool_toggled)
            root.addWidget(self.checkbox, alignment=Qt.AlignCenter)
            self.input = None
            self.save_button = None
            return

        form = QFormLayout()
        form.setSpacing(8)
        self.input = QLineEdit()
        if current_value is not None:
            self.input.setText(str(current_value))
        form.addRow("value", self.input)
        root.addLayout(form)

        self.save_button = QPushButton("save")
        self.save_button.setCursor(Qt.PointingHandCursor)
        self.save_button.clicked.connect(self._on_save)
        root.addWidget(self.save_button, alignment=Qt.AlignCenter)

    def _on_bool_toggled(self, checked: bool):
        self.result_value = 1.0 if checked else 0.0
        self.accept()

    def _on_save(self):
        # Только для числовых
        text = self.input.text().strip()
        try:
            self.result_value = float(text)
        except ValueError:
            QMessageBox.warning(self, "warning", "value must be a number")
            return
        self.accept()


class PageView(QWidget):
    back_requested = Signal()

    page_updated = Signal()   # после edit — нужно перерисовать и обновить список
    page_deleted = Signal()   # после delete — MainWindow уйдёт на home

    def __init__(self, parent=None):
        super().__init__(parent)
        self._page = None
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(20, 10, 20, 20)
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

        self.edit_button = QPushButton("edit")
        self.edit_button.setObjectName("editDeleteButton")
        self.edit_button.setCursor(Qt.PointingHandCursor)
        self.edit_button.clicked.connect(self._on_edit)

        self.delete_button = QPushButton("delete")
        self.delete_button.setObjectName("editDeleteButton")
        self.delete_button.setCursor(Qt.PointingHandCursor)
        self.delete_button.clicked.connect(self._on_delete)

        top.addWidget(self.edit_button)
        top.addWidget(self.delete_button)

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
            gold_min=self._page.gold_min,
            gold_max=self._page.gold_max,
            metric_type=self._page.metric_type,
        )
        self._rebuild_legend()

    def _rebuild_legend(self):
        while self.legend_layout.count():
            item = self.legend_layout.takeAt(0)
            w = item.widget()
            if w is not None:
                w.deleteLater()

        if self._page.metric_type == "bool":
            from .colors import BASE_COLORS
            base = BASE_COLORS.get(self._page.gradient, "#2ea043")

            self.legend_layout.addWidget(QLabel("not done"))
            empty = QLabel()
            empty.setFixedSize(14, 14)
            empty.setStyleSheet("background-color: #f5f5f5; border-radius: 3px;")
            self.legend_layout.addWidget(empty)

            self.legend_layout.addSpacing(16)

            self.legend_layout.addWidget(QLabel("done"))
            filled = QLabel()
            filled.setFixedSize(14, 14)
            filled.setStyleSheet(f"background-color: {base}; border-radius: 3px;")
            self.legend_layout.addWidget(filled)

            self.legend_layout.addStretch()
            return

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

        if self._page.gold_min is not None and self._page.gold_max is not None:
            gold = QLabel()
            gold.setFixedSize(14, 14)
            gold.setStyleSheet("background-color: #FFD700; border-radius: 3px;")
            self.legend_layout.addSpacing(16)
            self.legend_layout.addWidget(gold)
            self.legend_layout.addWidget(
                QLabel(f"gold {self._page.gold_min:g}–{self._page.gold_max:g}")
            )

        self.legend_layout.addStretch()

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
                gold_min=self._page.gold_min,
                gold_max=self._page.gold_max,
                metric_type=self._page.metric_type,
            )


    def _on_edit(self):
        if self._page is None:
            return
        dialog = EditPageDialog(self._page, parent=self)
        if dialog.exec() == QDialog.Accepted:
            # перечитать страницу из БД (могли поменять name/gradient/gold)
            self.load_page(self._page.id)
            self.page_updated.emit()

    def _on_delete(self):
        if self._page is None:
            return
        answer = QMessageBox.question(
            self,
            "delete page",
            f"delete '{self._page.name}' and all its entries?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if answer != QMessageBox.Yes:
            return
        page_id = self._page.id
        delete_page(page_id)
        self._page = None
        self.page_deleted.emit()