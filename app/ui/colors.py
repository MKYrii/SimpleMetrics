"""
Цвета и палитры.
10 базовых цветов. Для каждого генерируется 5 ступеней от светлого к тёмному.
"""

EMPTY_COLOR = "#f5f5f5"
TODAY_COLOR = "#ffffff"
GOLD_COLOR = "#FFD700"


def _hex_to_rgb(h: str) -> tuple[int, int, int]:
    h = h.lstrip("#")
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def _rgb_to_hex(r: int, g: int, b: int) -> str:
    r = max(0, min(255, r))
    g = max(0, min(255, g))
    b = max(0, min(255, b))
    return f"#{r:02x}{g:02x}{b:02x}"


def _lighten(rgb, factor):
    """factor 0..1, 1 = белый."""
    r, g, b = rgb
    return (
        int(r + (255 - r) * factor),
        int(g + (255 - g) * factor),
        int(b + (255 - b) * factor),
    )


def _darken(rgb, factor):
    """factor 0..1, 1 = чёрный."""
    r, g, b = rgb
    return int(r * (1 - factor)), int(g * (1 - factor)), int(b * (1 - factor))


def _build_palette(base_hex: str) -> list[str]:
    """5 ступеней: очень светлый -> очень тёмный."""
    rgb = _hex_to_rgb(base_hex)
    steps = [
        _lighten(rgb, 0.75),
        _lighten(rgb, 0.45),
        rgb,
        _darken(rgb, 0.35),
        _darken(rgb, 0.6),
    ]
    return [_rgb_to_hex(*s) for s in steps]


# 10 базовых цветов
BASE_COLORS: dict[str, str] = {
    "green":  "#2ea043",
    "red":    "#d1242f",
    "blue":   "#1f6feb",
    "purple": "#8957e5",
    "orange": "#e3791a",
    "teal":   "#1a9c8a",
    "pink":   "#e0568b",
    "indigo": "#3f51b5",
    "lime":   "#7cb342",
    "brown":  "#8b5e3c",
}

GRADIENTS: dict[str, list[str]] = {
    name: _build_palette(hex_) for name, hex_ in BASE_COLORS.items()
}


def value_to_color(
    value: float | None,
    min_value: float,
    max_value: float,
    gradient: str,
    gold_min: float | None,
    gold_max: float | None,
    is_today: bool = False,
) -> str:
    if value is None:
        return TODAY_COLOR if is_today else EMPTY_COLOR

    if gold_min is not None and gold_max is not None:
        if gold_min <= value <= gold_max:
            return GOLD_COLOR

    palette = GRADIENTS.get(gradient) or list(GRADIENTS.values())[0]

    if max_value <= min_value:
        idx = 0
    else:
        t = (value - min_value) / (max_value - min_value)
        t = max(0.0, min(1.0, t))
        idx = int(t * (len(palette) - 1))

    return palette[idx]


def legend_colors(gradient: str) -> list[str]:
    return GRADIENTS.get(gradient) or list(GRADIENTS.values())[0]