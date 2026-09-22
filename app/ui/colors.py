"""
Цвета и палитры.
Все палитры — 5 ступеней от светлого к тёмному (как github).
value_to_color возвращает hex-строку.
"""

# Светло-светло-серый для "нет записи"
EMPTY_COLOR = "#f5f5f5"
# Белый для "сегодня, но записи ещё нет"
TODAY_COLOR = "#ffffff"
# Золотой для "хорошего дня"
GOLD_COLOR = "#FFD700"

# Палитры: 5 цветов от слабого к сильному
GRADIENTS = {
    "green": ["#c6e48b", "#7bc96f", "#239a3b", "#196127", "#0e4429"],
    "red":   ["#fbc4c4", "#f28b8b", "#e04b4b", "#a82a2a", "#6b1414"],
    "blue":  ["#c3d9f5", "#8ab4ec", "#4a86d8", "#2a5aa8", "#123a6b"],
}


def value_to_color(
    value: float | None,
    min_value: float,
    max_value: float,
    gradient: str,
    gold_threshold: float | None,
    is_today: bool = False,
) -> str:
    """
    value=None  -> день без записи (серый или белый если сегодня).
    Иначе: нормализуем в 0..1, берём ступень палитры.
    Если gold_threshold задан и value >= него -> золотой.
    """
    if value is None:
        return TODAY_COLOR if is_today else EMPTY_COLOR

    if gold_threshold is not None and value >= gold_threshold:
        return GOLD_COLOR

    palette = GRADIENTS.get(gradient, GRADIENTS["green"])

    if max_value <= min_value:
        idx = 0
    else:
        t = (value - min_value) / (max_value - min_value)
        t = max(0.0, min(1.0, t))
        idx = int(t * (len(palette) - 1))

    return palette[idx]


def legend_colors(gradient: str) -> list[str]:
    """Список цветов палитры для отрисовки легенды."""
    return GRADIENTS.get(gradient, GRADIENTS["green"])