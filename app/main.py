"""
Точка входа.
Создаёт QApplication, ставит глобальный шрифт и QSS, открывает MainWindow.
"""

import sys
from PySide6.QtWidgets import QApplication

from ui.main_window import MainWindow
from ui.styles import get_app_font, GLOBAL_QSS

from app.database import init_db


def main():

    init_db()
    app = QApplication(sys.argv)
    app.setFont(get_app_font())
    app.setStyleSheet(GLOBAL_QSS)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()