"""
Глобальные стили и шрифт приложения.
Всё ч/б: белый фон, чёрный текст.
"""

from PySide6.QtGui import QFont


FONT_FAMILY = "Calibri"
FONT_SIZE = 14


def get_app_font() -> QFont:
    """Шрифт, который ставим глобально в QApplication."""
    return QFont(FONT_FAMILY, FONT_SIZE)


# QSS — стилизация виджетов. Синтаксис похож на CSS.
GLOBAL_QSS = """
QWidget {
    background-color: #ffffff;
    color: #000000;
    font-family: "Calibri";
    font-size: 14px;
}

/* Список страниц слева */
QListWidget {
    background-color: #ffffff;
    border: none;
    border-right: 1px solid #000000;
    outline: none;
}
QListWidget::item {
    padding: 8px;
}
QListWidget::item:selected {
    background-color: #000000;
    color: #ffffff;
}

/* Кнопка create — крупная, минималистичная */
QPushButton#createButton {
    background-color: #ffffff;
    color: #000000;
    border: 1px solid #000000;
    border-radius: 4px;
    padding: 10px 40px;
    font-size: 16px;
}
QPushButton#createButton:hover {
    background-color: #000000;
    color: #ffffff;
}

/* Круглые кнопки-стрелки */
QPushButton#roundButton {
    background-color: #ffffff;
    color: #000000;
    border: 1px solid #000000;
    border-radius: 20px;
    min-width: 40px;
    max-width: 40px;
    min-height: 40px;
    max-height: 40px;
    font-size: 18px;
}
QPushButton#roundButton:hover {
    background-color: #000000;
    color: #ffffff;
}

/* Крупный текст hello */
QLabel#helloLabel {
    font-size: 48px;
    color: #000000;
}

/* Заголовки экранов-заглушек */
QLabel#screenTitle {
    font-size: 28px;
    color: #000000;
}

/* Выезжающая панель со списком страниц */
QListWidget#pagesPanel {
    background-color: #f0f0f0;
    border: none;
    border-right: 1px solid #cccccc;
    outline: none;
    padding-top: 60px;
}
QListWidget#pagesPanel::item {
    padding: 10px 14px;
    margin: 4px 10px;
    color: #000000;
    border: 1px solid #000000;
    border-radius: 4px;
    background-color: #ffffff;
}
QListWidget#pagesPanel::item:hover {
    background-color: #e5e5e5;
}
QListWidget#pagesPanel::item:selected {
    background-color: #000000;
    color: #ffffff;
}

/* Кнопка-бургер (открыть список) */
QPushButton#burgerButton {
    background-color: #ffffff;
    color: #000000;
    border: 1px solid #000000;
    border-radius: 20px;
    min-width: 40px;
    max-width: 40px;
    min-height: 40px;
    max-height: 40px;
    font-size: 18px;
}
QPushButton#burgerButton:hover {
    background-color: #000000;
    color: #ffffff;
}


QDialog {
    background-color: #ffffff;
}

QLineEdit {
    border: 1px solid #000000;
    border-radius: 3px;
    padding: 6px 8px;
    background-color: #ffffff;
    color: #000000;
}

QComboBox {
    border: 1px solid #000000;
    border-radius: 3px;
    padding: 4px 8px;
    background-color: #ffffff;
    color: #000000;
}

QCheckBox {
    color: #000000;
}
"""