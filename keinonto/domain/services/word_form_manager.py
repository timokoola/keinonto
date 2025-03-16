"""Service for managing word forms and stems."""

from typing import Dict, Optional

from keinonto.domain.entities.word import Word
from keinonto.domain.interfaces.word_repository import IWordRepository
from keinonto.domain.value_objects.case import Case
from keinonto.domain.value_objects.number import Number
from keinonto.domain.value_objects.stem_type import StemType
from keinonto.domain.value_objects.word_form import WordDeclension


class WordFormManager:
    """Service for managing word forms and stems."""

    def __init__(self, repository: IWordRepository):
        """Initialize the service.

        Args:
            repository: Repository for storing words and stems
        """
        self._repository = repository

    async def add_word_with_forms(
        self,
        base_form: str,
        declension_class: int,
        forms_dict: Dict[str, str],
        gradation_type: Optional[str] = None,
    ) -> None:
        """Add a word along with its forms to the repository.

        Args:
            base_form: The dictionary form (nominative singular) of the word
            declension_class: The declension class number (1-51)
            forms_dict: Dictionary mapping case names to forms
            gradation_type: Optional gradation pattern (e.g. 'k-kk', 't-tt')

        Raises:
            ValueError: If forms are invalid or missing required forms
        """
        # Create word declension and extract stems
        declension = WordDeclension.from_forms_dict(
            base_form=base_form,
            declension_class=declension_class,
            forms_dict=forms_dict,
            gradation_type=gradation_type,
        )
        stems = declension.extract_stems()

        # Create and save word
        word = Word(
            base_form=base_form,
            declension_class=declension_class,
            gradation_type=gradation_type,
        )
        await self._repository.save_word(word)

        # Save stems
        for stem_type, stem in stems.items():
            await self._repository.save_stem(word, stem_type, stem)

    async def generate_form(
        self,
        word: Word,
        stems: Dict[StemType, str],
        case: Case,
        number: Number,
    ) -> str:
        """Generate a specific form of a word.

        Args:
            word: The word to generate a form for
            stems: Dictionary mapping stem types to their values
            case: The grammatical case to generate
            number: The grammatical number to generate

        Returns:
            The generated word form

        Raises:
            ValueError: If required stems are missing
        """
        # Example implementation - actual rules would be more complex
        if case == Case.NOMINATIVE:
            if number == Number.SINGULAR:
                return stems[StemType.STRONG]
            return stems[StemType.PLURAL] + "t"

        if case == Case.GENITIVE:
            if number == Number.SINGULAR:
                return stems[StemType.WEAK] + "n"
            return stems[StemType.PLURAL] + "ien"

        # Add more cases and rules as needed
        msg = f"Form generation not implemented for {case} {number}"
        raise ValueError(msg)

    async def save_stem(
        self,
        word: Word,  # pylint: disable=unused-argument
        stem_type: StemType,
        stem: str,
    ) -> None:
        """Save a stem for a word.

        Args:
            word: The word to save the stem for
            stem_type: Type of the stem
            stem: The stem value
        """
        # Not implemented in base class
        raise NotImplementedError("save_stem not implemented")
