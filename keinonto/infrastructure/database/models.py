"""Database models for SQLite."""

from typing import Optional

# pylint: disable=import-error,too-few-public-methods
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Base class for SQLAlchemy models."""


class WordModel(Base):
    """SQLAlchemy model for words."""

    __tablename__ = "words"

    id: Mapped[int] = mapped_column(primary_key=True)
    base_form: Mapped[str] = mapped_column(String(50))
    declension_class: Mapped[int]
    gradation_type: Mapped[Optional[str]] = mapped_column(String(10))

    stems = relationship("StemModel", back_populates="word")


class StemModel(Base):
    """SQLAlchemy model for word stems."""

    __tablename__ = "stems"

    id: Mapped[int] = mapped_column(primary_key=True)
    word_id: Mapped[int] = mapped_column(ForeignKey("words.id"))
    stem_type: Mapped[str] = mapped_column(String(20))
    stem: Mapped[str] = mapped_column(String(50))

    word = relationship("WordModel", back_populates="stems")
