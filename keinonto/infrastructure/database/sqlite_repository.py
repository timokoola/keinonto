"""SQLite word repository implementation."""

from typing import Dict, List, Optional, Tuple

# pylint: disable=import-error
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ...domain.entities.word import Word, WordStem
from ...domain.interfaces.word_repository import IWordRepository
from ...domain.value_objects.case import Case
from ...domain.value_objects.number import Number
from ...domain.value_objects.stem_type import StemType
from .models import StemModel, WordModel


class SQLiteWordRepository(IWordRepository):
    """SQLite word repository implementation."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize repository with database session."""
        self._session = session

    async def get_word(self, base_form: str) -> Optional[Word]:
        """Get a word from the repository by its base form."""
        stmt = (
            select(WordModel)
            .options(selectinload(WordModel.stems))
            .where(WordModel.base_form == base_form)
        )
        result = await self._session.execute(stmt)
        word_model = result.scalar_one_or_none()

        if word_model is None:
            return None

        return Word(
            base_form=word_model.base_form,
            declension_class=word_model.declension_class,
            gradation_type=word_model.gradation_type,
            stems=[
                WordStem(
                    stem_type=StemType(stem.stem_type),
                    value=stem.stem,
                )
                for stem in word_model.stems
            ],
        )

    async def get_form(
        self,
        word: Word,
        case: Case,
        number: Number,
    ) -> Optional[str]:
        """Get a specific form of a word."""
        # This is a placeholder implementation that returns None
        # The actual form generation will be handled by the WordGenerator
        return None

    async def get_all_forms(
        self,
        word: Word,
    ) -> List[Tuple[Case, Number, str]]:
        """Get all available forms for a word."""
        # This is a placeholder implementation that returns an empty list
        # The actual form generation will be handled by the WordGenerator
        return []

    async def get_stems(self, word: Word) -> Dict[StemType, str]:
        """Get all stems for a word.

        Args:
            word: The word to get stems for.

        Returns:
            A dictionary mapping stem types to their values.
        """
        query = (
            select(WordModel)
            .where(WordModel.base_form == word.base_form)
            .options(selectinload(WordModel.stems))
        )
        result = await self._session.execute(query)
        word_model = result.scalar_one_or_none()

        if word_model is None:
            return {}

        stems = {}
        for stem in word_model.stems:
            stems[StemType(stem.stem_type)] = stem.stem
        return stems

    async def save_word(self, word: Word) -> None:
        """Save a word to the repository."""
        word_model = WordModel(
            base_form=word.base_form,
            declension_class=word.declension_class,
            gradation_type=word.gradation_type,
        )
        self._session.add(word_model)
        await self._session.commit()

    async def save_stem(
        self,
        word: Word,
        stem_type: StemType,
        stem: str,
    ) -> None:
        """Save a word stem."""
        stmt = (
            select(WordModel)
            .options(selectinload(WordModel.stems))
            .where(WordModel.base_form == word.base_form)
        )
        result = await self._session.execute(stmt)
        word_model = result.scalar_one()

        # Check if stem already exists
        existing_stem = None
        for stem_model in word_model.stems:
            if stem_model.stem_type == stem_type.value:
                existing_stem = stem_model
                break

        if existing_stem:
            existing_stem.stem = stem
        else:
            # Create new stem
            stem_model = StemModel(
                word_id=word_model.id,
                stem_type=stem_type.value,
                stem=stem,
            )
            self._session.add(stem_model)
            word_model.stems.append(stem_model)

        await self._session.commit()
