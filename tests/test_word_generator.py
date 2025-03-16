"""
Tests for the WordGenerator class.
"""

import pytest
from typing import List, Optional, Tuple

from keinonto.domain.entities.word import Word
from keinonto.domain.interfaces.word_repository import IWordRepository
from keinonto.domain.value_objects.case import Case
from keinonto.domain.value_objects.number import Number
from keinonto.presentation.api.word_generator import WordGenerator


class MockWordRepository(IWordRepository):
    """Mock repository for testing."""
    
    async def get_word(self, base_form: str) -> Optional[Word]:
        if base_form == "sana":
            return Word(base_form="sana", declension_class=9)
        return None
    
    async def get_form(self, word: Word, case: Case, number: Number) -> Optional[str]:
        if word.base_form == "sana":
            if case == Case.INESSIVE and number == Number.PLURAL:
                return "sanoissa"
        return None
    
    async def get_all_forms(self, word: Word) -> List[Tuple[Case, Number, str]]:
        if word.base_form == "sana":
            return [
                (Case.NOMINATIVE, Number.SINGULAR, "sana"),
                (Case.INESSIVE, Number.PLURAL, "sanoissa"),
            ]
        return []
    
    async def save_word(self, word: Word) -> None:
        pass


@pytest.fixture
def generator():
    """Create a WordGenerator instance with mock repository."""
    return WordGenerator(MockWordRepository())


@pytest.mark.asyncio
async def test_generate_existing_word(generator):
    """Test generating a form for an existing word."""
    result = await generator.generate("sana", "inessive", "plural")
    assert result == "sanoissa"


@pytest.mark.asyncio
async def test_generate_nonexistent_word(generator):
    """Test generating a form for a non-existent word."""
    result = await generator.generate("nonexistent", "inessive", "plural")
    assert result is None


@pytest.mark.asyncio
async def test_get_all_forms_existing_word(generator):
    """Test getting all forms for an existing word."""
    forms = await generator.get_all_forms("sana")
    assert len(forms) == 2
    assert (Case.NOMINATIVE, Number.SINGULAR, "sana") in forms
    assert (Case.INESSIVE, Number.PLURAL, "sanoissa") in forms


@pytest.mark.asyncio
async def test_get_all_forms_nonexistent_word(generator):
    """Test getting all forms for a non-existent word."""
    forms = await generator.get_all_forms("nonexistent")
    assert forms == [] 