"""
Interface for word data storage and retrieval.
"""

from abc import ABC, abstractmethod
from typing import Optional, List

from ..entities.word import Word
from ..value_objects.case import Case
from ..value_objects.number import Number


class IWordRepository(ABC):
    """Interface for word storage and retrieval."""
    
    @abstractmethod
    async def get_word(self, base_form: str) -> Optional[Word]:
        """Retrieve a word by its base form."""
        pass
    
    @abstractmethod
    async def get_form(self, word: Word, case: Case, number: Number) -> Optional[str]:
        """Get a specific form of a word."""
        pass
    
    @abstractmethod
    async def get_all_forms(self, word: Word) -> List[tuple[Case, Number, str]]:
        """Get all available forms for a word."""
        pass
    
    @abstractmethod
    async def save_word(self, word: Word) -> None:
        """Save a new word or update existing one."""
        pass 