"""Interface for word data storage and retrieval."""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Tuple

from ..entities.word import Word
from ..value_objects.case import Case
from ..value_objects.number import Number
from ..value_objects.stem_type import StemType


class IWordRepository(ABC):
    """Interface for word storage and retrieval."""

    @abstractmethod
    async def get_word(self, base_form: str) -> Optional[Word]:
        """Retrieve a word by its base form."""

    @abstractmethod
    async def get_form(
        self,
        word: Word,
        case: Case,
        number: Number,
    ) -> Optional[str]:
        """Get a specific form of a word."""

    @abstractmethod
    async def get_all_forms(
        self,
        word: Word,
    ) -> List[Tuple[Case, Number, str]]:
        """Get all available forms for a word."""

    @abstractmethod
    async def get_stems(self, word: Word) -> Dict[StemType, str]:
        """Get all stems for a word."""

    @abstractmethod
    async def save_word(self, word: Word) -> None:
        """Save a new word or update existing one."""

    @abstractmethod
    async def save_stem(
        self,
        word: Word,
        stem_type: StemType,
        stem: str,
    ) -> None:
        """Save a stem for a word."""
