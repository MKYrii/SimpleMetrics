"""
Модальное окно редактирования страницы метрики.
Поля: name, gradient (10 цветов квадратиками), gold from/to (только для числовых типов).
Внизу по центру — save.
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QHBoxLayout, QFormLayout, QGridLayout,
    QMessageBox, QWidget,
)

from app.database import update_page
from .colors import BASE_COLORS


class ColorSwatch(QPushButton):
    """Квадратик-переключатель одного базового цвета."""

    def __init__(self, name: str, hex_color: str, parent=None):
        super().__init__(parent)
        self.color_name = name
        self.setFixedSize(28, 28)
        self.setCursor(Qt.PointingHandCursor)
        self.setCheckable(True)
        self.setStyleSheet(
            f"QPushButton {{"
            f"  background-color: {hex_color};"
            f"  border: 2px solid #cccccc;"
            f"  border-radius: 4px;"
            f"}}"
            f"QPushButton:checked {{"
            f"  border: 2px solid #000000;"
            f"}}"
        )


class EditPageDialog(QDialog):
    def __init__(self, page, parent=None):
        super().__init__(parent)
        self.page = page
        self.setWindowTitle("edit page")
        self.setModal(True)
        self.setMinimumWidth(380)
        self._selected_color = page.gradient
        self._build_ui()
        self._load_values()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(20, 20, 20, 20)
        root.setSpacing(16)

        title = QLabel("edit page")
        title.setObjectName("screenTitle")
        title.setAlignment(Qt.AlignCenter)

        form = QFormLayout()
        form.setSpacing(12)
        form.setLabelAlignment(Qt.AlignRight)

        self.name_input = QLineEdit()

        form.addRow("name", self.name_input)

        # --- Палитра ---
        palette_label = QLabel("gradient")
        self.palette_widget = QWidget()
        palette_layout = QGridLayout(self.palette_widget)
        palette_layout.setContentsMargins(0, 0, 0, 0)
        palette_layout.setSpacing(6)

        self._swatches: list[ColorSwatch] = []
        for i, (name, hex_color) in enumerate(BASE_COLORS.items()):
            sw = ColorSwatch(name, hex_color)
            sw.clicked.connect(lambda _, s=sw: self._on_color_selected(s))
            self._swatches.append(sw)
            palette_layout.addWidget(sw, i // 5, i % 5)

        form.addRow(palette_label, self.palette_widget)

        # --- Gold (только для числовых) ---
        self.gold_min_input = QLineEdit()
        self.gold_min_input.setPlaceholderText("empty = off")
        self.gold_max_input = QLineEdit()
        self.gold_max_input.setPlaceholderText("empty = off")

        self.gold_min_label = QLabel("gold from")
        self.gold_max_label = QLabel("gold to")

        form.addRow(self.gold_min_label, self.gold_min_input)
        form.addRow(self.gold_max_label, self.gold_max_input)

        self._form = form

        # --- Save ---
        self.save_button = QPushButton("save")
        self.save_button.setObjectName("createButton")
        self.save_button.setCursor(Qt.PointingHandCursor)
        self.save_button.clicked.connect(self._on_save)

        root.addWidget(title)
        root.addLayout(form)
        root.addWidget(self.save_button, alignment=Qt.AlignCenter)

    def _load_values(self):
        self.name_input.setText(self.page.name)

        # Палитра
        for sw in self._swatches:
            sw.setChecked(sw.color_name == self.page.gradient)

        # Gold только для не-bool
        is_numeric = self.page.metric_type != "bool"
        self.gold_min_label.setVisible(is_numeric)
        self.gold_min_input.setVisible(is_numeric)
        self.gold_max_label.setVisible(is_numeric)
        self.gold_max_input.setVisible(is_numeric)

        if is_numeric:
            if self.page.gold_min is not None:
                self.gold_min_input.setText(f"{self.page.gold_min:g}")
            if self.page.gold_max is not None:
                self.gold_max_input.setText(f"{self.page.gold_max:g}")

    def _on_color_selected(self, swatch: ColorSwatch):
        for sw in self._swatches:
            sw.setChecked(sw is swatch)
        self._selected_color = swatch.color_name

    def _on_save(self):
        name = self.name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "warning", "name cannot be empty")
            return

        gold_min = gold_max = None
        if self.page.metric_type != "bool":
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

        update_page(
            page_id=self.page.id,
            name=name,
            gradient=self._selected_color,
            gold_min=gold_min,
            gold_max=gold_max,
        )
        self.accept()