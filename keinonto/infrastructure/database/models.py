"""SQLAlchemy models for word storage."""

from typing import List, Optional

from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Base class for SQLAlchemy models."""


class WordModel(Base):
    """Model for storing word information."""

    __tablename__ = "words"

    id: Mapped[int] = mapped_column(primary_key=True)
    base_form: Mapped[str] = mapped_column(String(50), unique=True)
    declension_class: Mapped[int]
    gradation_type: Mapped[Optional[str]] = mapped_column(String(10))

    # Relationship to stems
    stems: Mapped[List["WordStemModel"]] = relationship(
        "WordStemModel",
        back_populates="word",
        cascade="all, delete-orphan",
    )


class WordStemModel(Base):
    """Model for storing word stems."""

    __tablename__ = "word_stems"

    id: Mapped[int] = mapped_column(primary_key=True)
    word_id: Mapped[int] = mapped_column(ForeignKey("words.id"))
    stem_type: Mapped[str] = mapped_column(String(20))
    stem: Mapped[str] = mapped_column(String(50))

    # Relationship to base word
    word: Mapped["WordModel"] = relationship(
        "WordModel",
        back_populates="stems",
    )

    __table_args__ = (
        UniqueConstraint("word_id", "stem_type", name="uq_word_stem_type"),
    )
