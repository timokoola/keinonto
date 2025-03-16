"""Value objects for word forms."""

from typing import Dict, Optional, Tuple

from keinonto.domain.value_objects.case import Case
from keinonto.domain.value_objects.number import Number
from keinonto.domain.value_objects.stem_type import StemType


class WordForm:
    """Value object for a word form."""

    def __init__(
        self,
        form: str,
        case: Case,
        number: Number,
        used_stem: Optional[StemType] = None,
    ) -> None:
        """Initialize a word form.

        Args:
            form: The actual word form
            case: The case of the form
            number: The number of the form
            used_stem: The stem type used to generate this form, if any
        """
        self.form = form
        self.case = case
        self.number = number
        self.used_stem = used_stem


class WordDeclension:
    """Value object for a word declension."""

    def __init__(
        self,
        base_form: str,
        declension_class: int,
        gradation_type: Optional[str] = None,
        forms: Optional[Dict[Tuple[Case, Number], str]] = None,
    ) -> None:
        """Initialize a word declension.

        Args:
            base_form: The base form of the word
            declension_class: The declension class number (1-51)
            gradation_type: The gradation pattern, if any
            forms: Dictionary mapping case-number tuples to forms
        """
        self.base_form = base_form
        self.declension_class = declension_class
        self.gradation_type = gradation_type
        self.forms = forms or {}

    def extract_stems(self) -> Dict[StemType, str]:
        """Extract stems from the word forms.

        The stem extraction logic depends on the declension class.
        Here are some examples:

        Class 1 (talo):
            - Strong stem: talo (from nominative)
            - Weak stem: talo (no gradation)
            - Plural stem: talo (from nominative plural 'talot')

        Class 2 (palvelu):
            - Strong stem: palvelu (from nominative)
            - Weak stem: palvelu (no gradation)
            - Plural stem: palvelu (from nominative plural 'palvelut')

        Class 3 (valtio):
            - Strong stem: valtio (from nominative)
            - Weak stem: valtio (no gradation)
            - Plural stem: valtio (from nominative plural 'valtiot')

        Class 4 (laatikko):
            - Strong stem: laatikko (from nominative)
            - Weak stem: laatiko (from genitive 'laatikon')
            - Plural stem: laatiko (from nominative plural 'laatikot')

        Returns:
            Dictionary mapping stem types to stems
        """
        stems: Dict[StemType, str] = {}
        nom_sg = self.forms.get((Case.NOMINATIVE, Number.SINGULAR))
        gen_sg = self.forms.get((Case.GENITIVE, Number.SINGULAR))
        nom_pl = self.forms.get((Case.NOMINATIVE, Number.PLURAL))

        if not nom_sg:
            return stems

        # Extract strong stem from nominative singular
        stems[StemType.STRONG] = nom_sg

        # Extract weak stem from genitive singular if available
        if gen_sg:
            weak_stem = gen_sg[:-1]  # Remove -n ending
            stems[StemType.WEAK] = weak_stem

        # Extract plural stem from nominative plural if available
        if nom_pl:
            plural_stem = nom_pl[:-1]  # Remove -t ending
            stems[StemType.PLURAL] = plural_stem

        return stems

    @classmethod
    def from_forms_dict(
        cls,
        base_form: str,
        declension_class: int,
        forms_dict: Dict[str, str],
        gradation_type: Optional[str] = None,
    ) -> "WordDeclension":
        """Create a WordDeclension from a dictionary of forms.

        Args:
            base_form: The base form of the word
            declension_class: The declension class number (1-51)
            forms_dict: Dictionary mapping case_number strings to forms
            gradation_type: The gradation pattern, if any

        Returns:
            A new WordDeclension instance

        Raises:
            ValueError: If case/number format is invalid
        """
        forms: Dict[Tuple[Case, Number], str] = {}

        for case_str, form in forms_dict.items():
            try:
                case_part, number_part = case_str.lower().split("_")
                case = Case(case_part)
                number = Number(number_part)
                forms[(case, number)] = form
            except ValueError as e:
                msg = (
                    f"Invalid case/number format: {case_str}\n"
                    "Format should be 'case_number' "
                    "(e.g., 'nominative_singular')"
                )
                raise ValueError(msg) from e

        return cls(
            base_form=base_form,
            declension_class=declension_class,
            gradation_type=gradation_type,
            forms=forms,
        )
