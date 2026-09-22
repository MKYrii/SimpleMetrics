"""
Работа с БД. SQLAlchemy 2.x, SQLite.
Сущности:
  - Page: страница метрики (название, тип, градиент, пороги)
  - Day:  запись за конкретный день (FK на Page)
"""

from datetime import date
from sqlalchemy import (
    create_engine, Column, Integer, String, Float, Date,
    ForeignKey, UniqueConstraint, select,
)
from sqlalchemy.orm import declarative_base, sessionmaker, relationship, Session


# --- Подключение ---
# Файл metrics.db создаётся в текущей рабочей директории.
DB_URL = "sqlite:///metrics.db"
engine = create_engine(DB_URL, echo=False, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)

Base = declarative_base()


# --- Модели ---
class Page(Base):
    __tablename__ = "pages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    metric_type = Column(String, nullable=False)   # 'bool' | 'count' | 'hours'
    gradient = Column(String, nullable=False)      # 'red' | 'green' | 'blue'
    gold_threshold = Column(Float, nullable=True)  # None = выключено
    min_value = Column(Float, nullable=False, default=0.0)
    max_value = Column(Float, nullable=False, default=10.0)

    days = relationship("Day", back_populates="page", cascade="all, delete-orphan")


class Day(Base):
    __tablename__ = "days"

    id = Column(Integer, primary_key=True, autoincrement=True)
    page_id = Column(Integer, ForeignKey("pages.id", ondelete="CASCADE"), nullable=False, index=True)
    date = Column(Date, nullable=False)            # дата записи
    value = Column(Float, nullable=False, default=0.0)
    value_type = Column(String, nullable=True)     # задел на будущее (например, 'raw'/'computed')

    page = relationship("Page", back_populates="days")

    __table_args__ = (
        UniqueConstraint("page_id", "date", name="uq_page_date"),
    )


def init_db():
    """Создать таблицы, если их нет. Вызывать один раз при старте приложения."""
    Base.metadata.create_all(engine)


# --- CRUD для Page ---
def create_page(
    name: str,
    metric_type: str,
    gradient: str,
    gold_threshold: float | None,
    min_value: float,
    max_value: float,
) -> int:
    """Создать страницу, вернуть её id."""
    with SessionLocal() as s:
        page = Page(
            name=name,
            metric_type=metric_type,
            gradient=gradient,
            gold_threshold=gold_threshold,
            min_value=min_value,
            max_value=max_value,
        )
        s.add(page)
        s.commit()
        return page.id


def get_all_pages() -> list[Page]:
    with SessionLocal() as s:
        return list(s.scalars(select(Page).order_by(Page.id)))


def get_page(page_id: int) -> Page | None:
    with SessionLocal() as s:
        return s.get(Page, page_id)


def delete_page(page_id: int) -> None:
    with SessionLocal() as s:
        page = s.get(Page, page_id)
        if page is not None:
            s.delete(page)
            s.commit()


# --- CRUD для Day ---
def set_day_value(page_id: int, day: date, value: float) -> None:
    """
    Записать/обновить значение за день.
    UNIQUE(page_id, date) гарантирует одну запись — если есть, обновляем.
    """
    with SessionLocal() as s:
        existing = s.scalar(
            select(Day).where(Day.page_id == page_id, Day.date == day)
        )
        if existing is not None:
            existing.value = value
        else:
            s.add(Day(page_id=page_id, date=day, value=value))
        s.commit()


def get_days_for_page(page_id: int) -> dict[date, float]:
    """Вернуть словарь {date: value} для страницы."""
    with SessionLocal() as s:
        rows = s.scalars(select(Day).where(Day.page_id == page_id)).all()
        return {row.date: row.value for row in rows}