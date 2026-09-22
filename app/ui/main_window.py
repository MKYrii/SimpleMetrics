"""
Главное окно.
- QStackedWidget: home / create_page
- Выезжающая панель со списком страниц (анимация по geometry)
- Кнопка-бургер (только на home) открывает/закрывает панель
"""

from PySide6.QtCore import Qt, QPropertyAnimation, QRect, QEasingCurve
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QStackedWidget, QPushButton,
    QVBoxLayout, QHBoxLayout, QGridLayout, QListWidget, QListWidgetItem,
)

from .home_page import HomePage
from .create_page import CreatePage
from .page_view import PageView


class MainWindow(QMainWindow):
    HOME_INDEX = 0
    CREATE_INDEX = 1

    PANEL_WIDTH = 260
    ANIM_DURATION = 220

    PAGE_VIEW_INDEX = 2

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("metrics")
        self.setMinimumSize(820, 480)
        self.resize(1536, 864)
        self._panel_open = False
        self._build_ui()
        self.stack.setCurrentIndex(self.HOME_INDEX)
        self._update_burger_visibility()
        self._connect_signals()
        self._setup_animation()
        self._update_burger_visibility()
        self._reload_pages_list()

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)

        grid = QGridLayout(central)
        grid.setContentsMargins(0, 0, 0, 0)

        self.stack = QStackedWidget()
        self.home_page = HomePage()
        self.create_page = CreatePage()
        self.page_view = PageView()

        self.stack.addWidget(self.home_page)     # 0
        self.stack.addWidget(self.create_page)   # 1
        self.stack.addWidget(self.page_view)  # 2
        grid.addWidget(self.stack, 0, 0)

        # Бургер — отдельный child поверх, чтобы raise_() работал независимо
        self.burger_button = QPushButton("≡", self)
        self.burger_button.setObjectName("burgerButton")
        self.burger_button.setCursor(Qt.PointingHandCursor)
        self.burger_button.setFixedSize(40, 40)
        self.burger_button.setGeometry(15, 10, 40, 40)
        self.burger_button.raise_()

        # Выезжающая панель
        self.pages_panel = QListWidget(self)
        self.pages_panel.setObjectName("pagesPanel")
        self.pages_panel.setFixedWidth(self.PANEL_WIDTH)
        self.pages_panel.setGeometry(
            QRect(-self.PANEL_WIDTH, 0, self.PANEL_WIDTH, self.height())
        )
        self.pages_panel.raise_()

    def _connect_signals(self):
        self.home_page.create_requested.connect(self._go_create)
        self.create_page.back_requested.connect(self._go_home)
        self.create_page.page_created.connect(self._on_page_created)
        self.burger_button.clicked.connect(self._toggle_panel)
        self.pages_panel.itemClicked.connect(self._on_page_selected)
        self.page_view.back_requested.connect(self._go_home)

    def _setup_animation(self):
        self.panel_anim = QPropertyAnimation(self.pages_panel, b"geometry")
        self.panel_anim.setDuration(self.ANIM_DURATION)
        self.panel_anim.setEasingCurve(QEasingCurve.OutCubic)


    def _on_page_selected(self, item):
        page_id = item.data(Qt.UserRole)
        if page_id is None:
            return
        self.page_view.load_page(page_id)
        self.stack.setCurrentIndex(self.PAGE_VIEW_INDEX)
        self._close_panel_if_open()
        self._update_burger_visibility()

    # --- Панель ---
    def _toggle_panel(self):
        start = self.pages_panel.geometry()
        if self._panel_open:
            end = QRect(-self.PANEL_WIDTH, 0, self.PANEL_WIDTH, self.height())
        else:
            end = QRect(0, 0, self.PANEL_WIDTH, self.height())
            # Панель поверх всего, но бургер — ещё выше
            self.pages_panel.raise_()
            self.burger_button.raise_()
        self.panel_anim.stop()
        self.panel_anim.setStartValue(start)
        self.panel_anim.setEndValue(end)
        self.panel_anim.start()
        self._panel_open = not self._panel_open

    def _close_panel_if_open(self):
        if self._panel_open:
            self._toggle_panel()

    # --- Навигация ---
    def _go_home(self):
        self.stack.setCurrentIndex(self.HOME_INDEX)
        self._update_burger_visibility()

    def _go_create(self):
        self._close_panel_if_open()
        self.stack.setCurrentIndex(self.CREATE_INDEX)
        self._update_burger_visibility()

    def _update_burger_visibility(self):
        def _update_burger_visibility(self):
            # Бургер виден на home и на page_view, скрыт на create_page
            self.burger_button.setVisible(
                self.stack.currentIndex() in (self.HOME_INDEX, self.PAGE_VIEW_INDEX)
            )

    def _on_page_created(self, page_id: int):
        # Пока просто возвращаемся на home. Список страниц обновим позже.
        self._reload_pages_list()
        self._go_home()


    def _reload_pages_list(self):
        from app.database import get_all_pages
        self.pages_panel.clear()
        for page in get_all_pages():
            item = QListWidgetItem(page.name.lower())
            item.setData(Qt.UserRole, page.id)
            self.pages_panel.addItem(item)

    # --- Ресайз ---
    def resizeEvent(self, event):
        super().resizeEvent(event)
        x = 0 if self._panel_open else -self.PANEL_WIDTH
        self.pages_panel.setGeometry(x, 0, self.PANEL_WIDTH, self.height())
        self.burger_button.raise_()