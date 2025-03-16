"""Tests for SQLite word repository."""

from typing import AsyncGenerator

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

from keinonto.domain.entities.word import Word
from keinonto.domain.value_objects.stem_type import StemType
from keinonto.infrastructure.database.config import create_engine
from keinonto.infrastructure.database.models import Base
from keinonto.infrastructure.database.sqlite_repository import SQLiteWordRepository


@pytest_asyncio.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Create a test database session."""
    engine = await create_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    session_factory = sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    session = session_factory()
    try:
        yield session
    finally:
        await session.close()
        await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def repository(
    db_session: AsyncSession,
) -> SQLiteWordRepository:
    """Create a test repository."""
    return SQLiteWordRepository(db_session)


@pytest.mark.asyncio
async def test_save_and_get_word(
    repository: SQLiteWordRepository,
) -> None:
    """Test saving and retrieving a word."""
    word = Word(
        base_form="talo",
        declension_class=1,
        gradation_type=None,
    )
    await repository.save_word(word)

    result = await repository.get_word("talo")
    assert result is not None
    assert result.base_form == "talo"
    assert result.declension_class == 1
    assert result.gradation_type is None


@pytest.mark.asyncio
async def test_save_and_get_stems(
    repository: SQLiteWordRepository,
) -> None:
    """Test saving and retrieving word stems."""
    word = Word(
        base_form="talo",
        declension_class=1,
        gradation_type=None,
    )
    await repository.save_word(word)

    # Save stems
    async def save_stem() -> None:
        await repository.save_stem(word, StemType.STRONG, "talo")

    await save_stem()

    async def save_weak_stem() -> None:
        await repository.save_stem(word, StemType.WEAK, "talo")

    await save_weak_stem()

    result = await repository.get_word("talo")
    assert result is not None
    assert len(result.stems) == 2


@pytest.mark.asyncio
async def test_update_stem(
    repository: SQLiteWordRepository,
) -> None:
    """Test updating an existing word stem."""
    word = Word(
        base_form="katu",
        declension_class=1,
        gradation_type="t-d",
    )
    await repository.save_word(word)

    # Save initial stem
    async def save_stem() -> None:
        await repository.save_stem(word, StemType.STRONG, "katu")

    await save_stem()

    # Update stem
    async def update_stem() -> None:
        await repository.save_stem(word, StemType.STRONG, "kadu")

    await update_stem()

    result = await repository.get_word("katu")
    assert result is not None
    assert len(result.stems) == 1
    assert result.stems[0].value == "kadu"


@pytest.mark.asyncio
async def test_nonexistent_word(
    repository: SQLiteWordRepository,
) -> None:
    """Test retrieving a nonexistent word."""
    result = await repository.get_word("nonexistent")
    assert result is None
