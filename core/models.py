from datetime import datetime
from typing import Optional

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from core.database import Base


class MovieShowing(Base):
    __tablename__ = "movie_showing"

    id: Mapped[int] = mapped_column(primary_key=True)
    cinema: Mapped[str] = mapped_column(String(30))
    title: Mapped[str] = mapped_column(String(80))
    time: Mapped[datetime]
    cast = mapped_column(Text, nullable=True)
    summary = mapped_column(Text, nullable=True)
    genre: Mapped[Optional[str]] = mapped_column(String(30))
    language: Mapped[Optional[str]] = mapped_column(String(30))

    def __repr__(self) -> str:
        return f"Film {self.title!r}, Kino {self.cinema}, Zeit {self.time}"
