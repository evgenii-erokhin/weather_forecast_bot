from datetime import datetime

from sqlalchemy import DateTime, Index, Integer
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Coordinates(Base):
    __tablename__ = "coordinates"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    first_name: Mapped[str]
    username: Mapped[str]
    chat_id: Mapped[int]
    latitude: Mapped[float]
    longitude: Mapped[float]
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now, onupdate=datetime.now
    )

    __table_args__ = (
        Index("ix_coordinates_username_chat_id", "username", "chat_id", unique=True),
    )
