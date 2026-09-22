"""
Сетка 365 квадратов (heatmap) для одной страницы.
- 7 строк (пн..вс) × 53 колонки (недели)
- подписи месяцев сверху, дней недели слева
- клик по квадрату -> сигнал day_clicked(date)
"""

from datetime import date, timedelta

from PySide6.QtCore import Qt, Signal, QRectF, QPointF
from PySide6.QtGui import QPainter, QColor, QBrush, QFont, QPen
from PySide6.QtWidgets import QWidget

from .colors import value_to_color


CELL_SIZE = 12
CELL_GAP = 3
CELL_RADIUS = 3
LEFT_LABEL_WIDTH = 34
TOP_LABEL_HEIGHT = 20


class HeatmapWidget(QWidget):
    day_clicked = Signal(date)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMouseTracking(True)
        self.setMinimumSize(700, 160)

        # Данные текущей страницы (заполняются извне через set_data)
        self._values: dict[date, float] = {}
        self._min_value = 0.0
        self._max_value = 10.0
        self._gradient = "green"
        self._gold_threshold: float | None = None

        # Сетка строится один раз под текущую дату
        self._weeks = self._build_grid(date.today())
        # Карта: date -> (col, row) для быстрого поиска при клике
        self._date_to_cell: dict[date, tuple[int, int]] = {}
        for col, week in enumerate(self._weeks):
            for row, day in enumerate(week):
                if day is not None:
                    self._date_to_cell[day] = (col, row)

        self.setMinimumWidth(
            LEFT_LABEL_WIDTH + len(self._weeks) * (CELL_SIZE + CELL_GAP)
        )

    # --- Публичное API ---
    def set_data(
        self,
        values: dict[date, float],
        min_value: float,
        max_value: float,
        gradient: str,
        gold_threshold: float | None,
    ):
        self._values = values
        self._min_value = min_value
        self._max_value = max_value
        self._gradient = gradient
        self._gold_threshold = gold_threshold
        self.update()

    # --- Построение сетки ---
    def _build_grid(self, today: date) -> list[list[date | None]]:
        start = today - timedelta(days=364)
        start_aligned = start - timedelta(days=start.weekday())
        end_aligned = today + timedelta(days=(6 - today.weekday()))

        weeks: list[list[date | None]] = []
        current = start_aligned
        while current <= end_aligned:
            week: list[date | None] = []
            for i in range(7):
                d = current + timedelta(days=i)
                week.append(d if start <= d <= today else None)
            weeks.append(week)
            current += timedelta(days=7)
        return weeks

    # --- Координаты ---
    def _cell_rect(self, col: int, row: int) -> QRectF:
        x = LEFT_LABEL_WIDTH + col * (CELL_SIZE + CELL_GAP)
        y = TOP_LABEL_HEIGHT + row * (CELL_SIZE + CELL_GAP)
        return QRectF(x, y, CELL_SIZE, CELL_SIZE)

    def _cell_at(self, pos: QPointF) -> date | None:
        for d, (col, row) in self._date_to_cell.items():
            if self._cell_rect(col, row).contains(pos):
                return d
        return None

    # --- Отрисовка ---
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(Qt.NoPen)

        today = date.today()

        # Подписи месяцев сверху
        painter.setPen(QPen(QColor("#000000")))
        font = QFont("Calibri", 9)
        painter.setFont(font)

        prev_month = None
        for col, week in enumerate(self._weeks):
            first_day = next((d for d in week if d is not None), None)
            if first_day and first_day.month != prev_month:
                prev_month = first_day.month
                x = LEFT_LABEL_WIDTH + col * (CELL_SIZE + CELL_GAP)
                painter.drawText(
                    QPointF(x, TOP_LABEL_HEIGHT - 6),
                    first_day.strftime("%b").lower(),
                )

        # Подписи дней недели слева (только пн / ср / пт, как у гитхаба)
        for row, label in [(0, "mon"), (2, "wed"), (4, "fri")]:
            y = TOP_LABEL_HEIGHT + row * (CELL_SIZE + CELL_GAP) + CELL_SIZE - 2
            painter.drawText(QPointF(0, y), label)

        # Квадраты
        painter.setPen(Qt.NoPen)
        for d, (col, row) in self._date_to_cell.items():
            value = self._values.get(d)
            is_today = (d == today)
            color = value_to_color(
                value=value,
                min_value=self._min_value,
                max_value=self._max_value,
                gradient=self._gradient,
                gold_threshold=self._gold_threshold,
                is_today=is_today,
            )
            painter.setBrush(QBrush(QColor(color)))
            painter.drawRoundedRect(self._cell_rect(col, row), CELL_RADIUS, CELL_RADIUS)

    # --- Клик ---
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            d = self._cell_at(event.position())
            if d is not None:
                self.day_clicked.emit(d)