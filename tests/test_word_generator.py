"""Tests for word form generation."""

from typing import Dict, List, Optional, Tuple

import pytest
from pytest import fixture

from keinonto.domain.entities.word import Word
from keinonto.domain.interfaces.word_repository import IWordRepository
from keinonto.domain.value_objects.case import Case
from keinonto.domain.value_objects.number import Number
from keinonto.domain.value_objects.stem_type import StemType
from keinonto.presentation.api.word_generator import WordGenerator


class MockWordRepository(IWordRepository):
    """Mock implementation of word repository for testing."""

    async def get_word(self, base_form: str) -> Optional[Word]:
        """Get a word from the repository."""
        if base_form == "kissa":
            return Word(
                base_form="kissa",
                declension_class=1,
                gradation_type=None,
            )
        return None

    async def get_stems(self, word: Word) -> Dict[StemType, str]:
        """Get all stems for a word."""
        if word.base_form == "kissa":
            return {
                StemType.STRONG: "kissa",
                StemType.WEAK: "kissa",
            }
        return {}

    async def save_word(self, word: Word) -> None:
        """Save a word to the repository."""

    async def save_stem(
        self,
        word: Word,
        stem_type: StemType,
        stem: str,
    ) -> None:
        """Save a stem for a word."""

    async def get_form(
        self,
        word: Word,
        case: Case,
        number: Number,
    ) -> Optional[str]:
        """Get a specific form for a word."""
        if (
            word.base_form == "kissa"
            and case == Case.INESSIVE
            and number == Number.SINGULAR
        ):
            return "kissassa"
        return None

    async def get_all_forms(
        self,
        word: Word,
    ) -> List[Tuple[Case, Number, str]]:
        """Get all forms for a word."""
        if word.base_form == "kissa":
            return [(Case.INESSIVE, Number.SINGULAR, "kissassa")]
        return []


@fixture(scope="function")
def generator() -> WordGenerator:
    """Create a word generator for testing."""
    return WordGenerator(MockWordRepository())


@pytest.mark.asyncio
async def test_generate_existing_word(
    generator: WordGenerator,
) -> None:
    """Test generating forms for an existing word."""
    form = await generator.generate("kissa", Case.INESSIVE, Number.SINGULAR)
    assert form == "kissassa"


@pytest.mark.asyncio
async def test_generate_nonexistent_word(
    generator: WordGenerator,
) -> None:
    """Test generating forms for a nonexistent word."""
    form = await generator.generate("koira", Case.INESSIVE, Number.SINGULAR)
    assert form is None


@pytest.mark.asyncio
async def test_get_all_forms_existing_word(
    generator: WordGenerator,
) -> None:
    """Test getting all forms for an existing word."""
    forms = await generator.get_all_forms("kissa")
    assert len(forms) > 0


@pytest.mark.asyncio
async def test_get_all_forms_nonexistent_word(
    generator: WordGenerator,
) -> None:
    """Test getting all forms for a nonexistent word."""
    forms = await generator.get_all_forms("koira")
    assert len(forms) == 0
