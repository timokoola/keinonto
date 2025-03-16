"""Main API for Finnish word form generation."""

from typing import List, Optional, Tuple, Union

from ...domain.interfaces.word_repository import IWordRepository
from ...domain.value_objects.case import Case
from ...domain.value_objects.number import Number


class WordGenerator:
    """Main class for generating Finnish word forms."""

    def __init__(self, repository: IWordRepository):
        """Initialize the word generator with a repository."""
        self._repository = repository

    async def generate(
        self,
        word: str,
        case: Union[str, Case],
        number: Union[str, Number] = Number.SINGULAR,
    ) -> Optional[str]:
        """
        Generate a specific form of a Finnish word.

        Args:
            word: Base form of the word
            case: Target case (e.g., "inessive", Case.INESSIVE)
            number: Grammatical number (singular/plural)

        Returns:
            The generated word form or None if not possible

        Example:
            >>> generator = WordGenerator(repository)
            >>> await generator.generate("talo", "inessive", "singular")
            'talossa'
        """
        # Convert string inputs to enums if needed
        if isinstance(case, str):
            case = Case(case.lower())
        if isinstance(number, str):
            number = Number(number.lower())

        # Get word data from repository
        word_data = await self._repository.get_word(word)
        if not word_data:
            return None

        # Get the form from repository
        return await self._repository.get_form(word_data, case, number)

    async def get_all_forms(self, word: str) -> List[Tuple[Case, Number, str]]:
        """
        Get all available forms for a word.

        Args:
            word: Base form of the word

        Returns:
            List of tuples containing (case, number, form)
        """
        word_data = await self._repository.get_word(word)
        if not word_data:
            return []

        # Get all forms from repository
        return await self._repository.get_all_forms(word_data)
