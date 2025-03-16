"""Command line interface for quick testing."""

import argparse
import asyncio
import json
import sys
from typing import Dict, List, NoReturn, Optional, Tuple

from keinonto.domain.services.word_form_manager import WordFormManager
from keinonto.domain.value_objects.case import Case
from keinonto.domain.value_objects.number import Number
from keinonto.domain.value_objects.stem_type import StemType
from keinonto.infrastructure.database import sqlite_repository as repo
from keinonto.infrastructure.database.config import get_session
from keinonto.presentation.api.word_generator import WordGenerator


class CLIError(Exception):
    """Base class for CLI errors."""


class FormValidationError(CLIError):
    """Error raised when form validation fails."""


class GradationError(FormValidationError):
    """Error raised when gradation pattern validation fails."""


class VowelHarmonyError(FormValidationError):
    """Error raised when vowel harmony validation fails."""


class CaseNumberFormatError(FormValidationError):
    """Error raised when case/number format is invalid."""


class EndingError(FormValidationError):
    """Error raised when form ending is invalid."""


class FileError(CLIError):
    """Error raised when there are issues with file operations."""


class ValidationError(CLIError):
    """Error raised when validation fails."""


# Constants
REQUIRED_FORMS = [
    "nominative_singular",  # Base form
    "genitive_singular",  # For weak stem
    "partitive_singular",  # For special stems
    "nominative_plural",  # For plural stem
    "inessive_singular",  # For locative cases
    "illative_singular",  # For special illative handling
]

GRADATION_PATTERNS = {
    "pp-p": {"strong": "pp", "weak": "p"},
    "tt-t": {"strong": "tt", "weak": "t"},
    "kk-k": {"strong": "kk", "weak": "k"},
    "p-v": {"strong": "p", "weak": "v"},
    "t-d": {"strong": "t", "weak": "d"},
    "k-v": {"strong": "k", "weak": "v"},
    "k-j": {"strong": "k", "weak": "j"},
    "k-": {"strong": "k", "weak": ""},  # k disappears
    "nk-ng": {"strong": "nk", "weak": "ng"},
    "mp-mm": {"strong": "mp", "weak": "mm"},
    "nt-nn": {"strong": "nt", "weak": "nn"},
    "lt-ll": {"strong": "lt", "weak": "ll"},
    "rt-rr": {"strong": "rt", "weak": "rr"},
}

STRONG_GRADE_CASES = {
    (Case.NOMINATIVE, Number.SINGULAR),
    (Case.PARTITIVE, Number.SINGULAR),
    (Case.PARTITIVE, Number.PLURAL),
}

WEAK_GRADE_CASES = {
    (Case.GENITIVE, Number.SINGULAR),
    (Case.INESSIVE, Number.SINGULAR),
    (Case.ELATIVE, Number.SINGULAR),
    (Case.ILLATIVE, Number.SINGULAR),
    (Case.ADESSIVE, Number.SINGULAR),
    (Case.ABLATIVE, Number.SINGULAR),
    (Case.ALLATIVE, Number.SINGULAR),
}

CASE_RULES: Dict[Case, Dict[Number, List[str]]] = {
    Case.NOMINATIVE: {
        Number.SINGULAR: [],  # No specific ending required
        Number.PLURAL: ["t"],
    },
    Case.GENITIVE: {
        Number.SINGULAR: ["n"],
        Number.PLURAL: ["en", "in", "jen", "den", "tten", "ten"],
    },
    Case.PARTITIVE: {
        Number.SINGULAR: ["a", "ä", "ta", "tä"],
        Number.PLURAL: ["a", "ä", "ta", "tä", "ja", "jä"],
    },
    Case.INESSIVE: {
        Number.SINGULAR: ["ssa", "ssä"],
        Number.PLURAL: ["issa", "issä"],
    },
    Case.ELATIVE: {
        Number.SINGULAR: ["sta", "stä"],
        Number.PLURAL: ["ista", "istä"],
    },
    Case.ILLATIVE: {
        Number.SINGULAR: [
            "an",
            "än",
            "en",
            "in",
            "on",
            "ön",
            "un",
            "yn",
            "seen",
            "han",
            "hen",
        ],
        Number.PLURAL: ["iin", "ihin"],
    },
    Case.ADESSIVE: {
        Number.SINGULAR: ["lla", "llä"],
        Number.PLURAL: ["illa", "illä"],
    },
    Case.ABLATIVE: {
        Number.SINGULAR: ["lta", "ltä"],
        Number.PLURAL: ["ilta", "iltä"],
    },
    Case.ALLATIVE: {
        Number.SINGULAR: ["lle"],
        Number.PLURAL: ["ille"],
    },
    Case.ESSIVE: {
        Number.SINGULAR: ["na", "nä"],
        Number.PLURAL: ["ina", "inä"],
    },
    Case.TRANSLATIVE: {
        Number.SINGULAR: ["ksi"],
        Number.PLURAL: ["iksi"],
    },
    Case.INSTRUCTIVE: {
        Number.PLURAL: ["in"],
    },
    Case.ABESSIVE: {
        Number.SINGULAR: ["tta", "ttä"],
        Number.PLURAL: ["itta", "ittä"],
    },
    Case.COMITATIVE: {
        Number.PLURAL: ["ine"],  # Note: Always requires possessive suffix
    },
}


def load_json_forms(file_path: str) -> Dict[str, str]:
    """Load forms from a JSON file.

    Args:
        file_path: Path to the JSON file containing word forms

    Returns:
        Dictionary mapping case_number strings to word forms

    Raises:
        FileError: If there are issues reading or parsing the file
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            forms = json.load(f)
    except json.JSONDecodeError as e:
        raise FileError(f"Invalid JSON format: {str(e)}") from e
    except OSError as e:
        raise FileError(f"Error reading file: {str(e)}") from e

    if not isinstance(forms, dict):
        raise FileError("Forms file must contain a dictionary")

    return forms


def validate_required_forms(forms: Dict[str, str]) -> None:
    """Validate that all required forms are present.

    Args:
        forms: Dictionary mapping case_number strings to word forms

    Raises:
        FormValidationError: If required forms are missing
    """
    missing = [form for form in REQUIRED_FORMS if form not in forms]
    if missing:
        msg = (
            f"Missing required forms: {', '.join(missing)}\n"
            "These forms are needed for proper stem extraction"
        )
        raise FormValidationError(msg)


def detect_gradation_pattern(
    nom_sg: str,
    gen_sg: str,
) -> Optional[str]:
    """Detect gradation pattern from nominative and genitive forms.

    Args:
        nom_sg: Nominative singular form
        gen_sg: Genitive singular form

    Returns:
        Optional[str]: Detected gradation pattern or None if no pattern found
    """
    for pattern, changes in GRADATION_PATTERNS.items():
        if (changes["strong"] in nom_sg and changes["weak"] in gen_sg) or (
            pattern == "k-" and "k" in nom_sg and "k" not in gen_sg
        ):
            return pattern
    return None


def validate_gradation(
    form: str,
    case_str: str,
    case: Case,
    number: Number,
    detected_pattern: Optional[str],
) -> None:
    """Validate gradation pattern in a form.

    Args:
        form: Word form to validate
        case_str: Original case string from input
        case: Case of the form
        number: Number of the form
        detected_pattern: Detected gradation pattern or None

    Raises:
        GradationError: If gradation pattern validation fails
    """
    if not detected_pattern:
        return

    if (case, number) in STRONG_GRADE_CASES:
        pattern_rules = GRADATION_PATTERNS[detected_pattern]
        strong_grade = pattern_rules["strong"]
        if pattern_rules["strong"] not in form and detected_pattern != "k-":
            msg = (
                f"Gradation error in {case_str}: {form}\n"
                f"Expected strong grade '{strong_grade}' "
                f"for {case.value} {number.value}"
            )
            raise GradationError(msg)
        if detected_pattern == "k-" and "k" not in form:
            msg = (
                f"Gradation error in {case_str}: {form}\n"
                f"Expected 'k' for {case.value} {number.value}"
            )
            raise GradationError(msg)

    if (case, number) in WEAK_GRADE_CASES:
        pattern_rules = GRADATION_PATTERNS[detected_pattern]
        weak_grade = pattern_rules["weak"]
        if pattern_rules["weak"] not in form and detected_pattern != "k-":
            msg = (
                f"Gradation error in {case_str}: {form}\n"
                f"Expected weak grade '{weak_grade}' "
                f"for {case.value} {number.value}"
            )
            raise GradationError(msg)
        if detected_pattern == "k-" and "k" in form:
            msg = (
                f"Gradation error in {case_str}: {form}\n"
                f"Expected 'k' to disappear in "
                f"{case.value} {number.value}"
            )
            raise GradationError(msg)


def validate_vowel_harmony(
    form: str,
    valid_endings: List[str],
) -> None:
    """Validate vowel harmony in a form.

    Args:
        form: Word form to validate
        valid_endings: List of valid endings for this case and number

    Raises:
        VowelHarmonyError: If vowel harmony validation fails
    """
    if not valid_endings:
        return

    stem_part = form[: -len(valid_endings[0])]

    if any(ending in ["a", "o", "u"] for ending in valid_endings):
        # Back vowel endings should only be used with back vowel words
        front_vowels = set("äöy")
        if any(c in front_vowels for c in stem_part):
            msg = (
                f"Vowel harmony mismatch in {form}\n"
                "Back vowel endings used with front vowel stem"
            )
            raise VowelHarmonyError(msg)

    elif any(ending in ["ä", "ö", "y"] for ending in valid_endings):
        # Front vowel endings should only be used with front vowel words
        back_vowels = set("aou")
        if any(c in back_vowels for c in stem_part):
            msg = (
                f"Vowel harmony mismatch in {form}\n"
                "Front vowel endings used with back vowel stem"
            )
            raise VowelHarmonyError(msg)


def validate_form_ending(
    form: str,
    case: Case,
    number: Number,
    valid_endings: List[str],
) -> None:
    """Validate form ending.

    Args:
        form: Word form to validate
        case: Case of the form
        number: Number of the form
        valid_endings: List of valid endings for this case and number

    Raises:
        EndingError: If form ending validation fails
    """
    if not valid_endings:
        return

    if not any(form.endswith(ending) for ending in valid_endings):
        endings_str = "', '".join(valid_endings)
        msg = (
            f"Invalid {case.value} {number.value} form: {form}\n"
            f"Form should end in one of: '{endings_str}'"
        )
        raise EndingError(msg)

    if case == Case.COMITATIVE and number == Number.PLURAL:
        endings = ["i", "e"]
        has_possessive = any(form.endswith(f"{e}en") for e in endings)
        if not has_possessive:
            msg = (
                f"Invalid comitative form: {form}\n"
                "Comitative forms require a possessive suffix (-en)"
            )
            raise EndingError(msg)


def parse_case_number(case_str: str) -> Tuple[Case, Number]:
    """Parse case and number from a string.

    Args:
        case_str: String in format "case_number"
        Example: "nominative_singular"

    Returns:
        Tuple of parsed case and number

    Raises:
        CaseNumberFormatError: If case/number format is invalid
    """
    try:
        case_part, number_part = case_str.lower().split("_")
        return Case(case_part), Number(number_part)
    except ValueError as e:
        msg = (
            f"Invalid case/number format: {case_str}\n"
            "Format should be 'case_number' "
            "(e.g., 'nominative_singular')"
        )
        raise CaseNumberFormatError(msg) from e


def validate_form(
    case_str: str,
    form: str,
    detected_pattern: Optional[str],
) -> None:
    """Validate a single form.

    Args:
        case_str: String in format case_number
        form: Word form to validate
        detected_pattern: Detected gradation pattern or None

    Raises:
        FormValidationError: If validation fails
        GradationError: If gradation pattern validation fails
        VowelHarmonyError: If vowel harmony validation fails
        CaseNumberFormatError: If case/number format is invalid
        EndingError: If form ending is invalid
    """
    if not isinstance(form, str):
        raise FormValidationError(f"Form must be a string: {case_str}")
    if not form:
        raise FormValidationError(f"Empty form not allowed: {case_str}")

    case, number = parse_case_number(case_str)

    validate_gradation(form, case_str, case, number, detected_pattern)

    if case not in CASE_RULES or number not in CASE_RULES[case]:
        return

    valid_endings = CASE_RULES[case][number]
    validate_form_ending(form, case, number, valid_endings)
    validate_vowel_harmony(form, valid_endings)


def stem_type_arg(value: str) -> str:
    """Convert stem type argument to proper format.

    Args:
        value: The stem type value to convert

    Returns:
        The normalized stem type value

    Raises:
        ArgumentTypeError: If the value is not a valid stem type
    """
    normalized = value.lower()
    valid_types = [t.value for t in StemType]
    if normalized not in valid_types:
        types_str = ", ".join(valid_types)
        msg = f"Invalid stem type. Choose from: {types_str}"
        raise argparse.ArgumentTypeError(msg)
    return normalized


def case_type(value: str) -> str:
    """Convert case argument to proper format."""
    normalized = value.lower()
    valid_cases = [c.value for c in Case]
    if normalized not in valid_cases:
        cases_str = ", ".join(valid_cases)
        msg = f"Invalid case. Choose from: {cases_str}"
        raise argparse.ArgumentTypeError(msg)
    return normalized


def load_forms(file_path: str) -> Dict[str, str]:
    """Load and validate word forms from a JSON file.

    The JSON file should contain a dictionary mapping case names to forms.
    Example format:
    {
        "nominative_singular": "talo",
        "genitive_singular": "talon",
        "partitive_singular": "taloa",
        ...
    }

    Args:
        file_path: Path to the JSON file containing word forms

    Returns:
        Dictionary mapping case_number strings to word forms

    Raises:
        CLIError: If the file format is invalid
        FormValidationError: If forms validation fails
        GradationError: If gradation pattern validation fails
        VowelHarmonyError: If vowel harmony validation fails
        CaseNumberFormatError: If case/number format is invalid
        EndingError: If form ending is invalid
    """
    forms = load_json_forms(file_path)
    validate_required_forms(forms)

    detected_pattern = detect_gradation_pattern(
        forms.get("nominative_singular", ""),
        forms.get("genitive_singular", ""),
    )

    for case_str, form in forms.items():
        validate_form(case_str, form, detected_pattern)

    return forms


def create_parser() -> argparse.ArgumentParser:
    """Create the argument parser for the CLI."""
    desc = "CLI for testing word form generation"
    parser = argparse.ArgumentParser(description=desc)
    subparsers = parser.add_subparsers(dest="command")

    # Add word with forms
    add_forms = subparsers.add_parser(
        "add-forms",
        help="Add a word with its forms from a JSON file",
    )
    add_forms.add_argument("base_form", help="Base form of the word")
    add_forms.add_argument(
        "declension_class",
        type=int,
        help="Declension class number (1-51)",
    )
    add_forms.add_argument(
        "forms_file",
        help="JSON file containing word forms",
    )
    add_forms.add_argument(
        "--gradation",
        help="Gradation pattern (e.g., 'k-kk', 't-tt')",
    )

    # Add stem
    add_stem = subparsers.add_parser(
        "add-stem",
        help="Add a stem for a word",
    )
    add_stem.add_argument("base_form", help="Base form of the word")
    add_stem.add_argument(
        "stem_type",
        type=stem_type_arg,
        help="Type of the stem",
    )
    add_stem.add_argument("stem", help="The stem value")

    # Get word info
    info = subparsers.add_parser(
        "info",
        help="Get information about a word",
    )
    info.add_argument("base_form", help="Base form of the word")

    # Generate form
    gen = subparsers.add_parser(
        "gen",
        help="Generate a specific form of a word",
    )
    gen.add_argument("base_form", help="Base form of the word")
    gen.add_argument(
        "case",
        type=case_type,
        help="Case to generate",
    )

    return parser


async def add_word_with_forms(
    manager: WordFormManager,
    args: argparse.Namespace,
) -> None:
    """Add a word with its forms to the repository."""
    forms = load_forms(args.forms_file)
    await manager.add_word_with_forms(
        base_form=args.base_form,
        declension_class=args.declension_class,
        forms_dict=forms,
        gradation_type=args.gradation,
    )
    print(f"Added word '{args.base_form}' with forms")


async def add_word_stem(
    repository: repo.SQLiteWordRepository,
    args: argparse.Namespace,
) -> None:
    """Add a stem for a word."""
    word = await repository.get_word(args.base_form)
    if not word:
        raise CLIError(f"Word '{args.base_form}' not found")

    await repository.save_stem(
        word=word,
        stem_type=StemType(args.stem_type),
        stem=args.stem,
    )
    print(f"Added {args.stem_type} stem for '{args.base_form}'")


async def get_word_info(
    repository: repo.SQLiteWordRepository,
    args: argparse.Namespace,
) -> None:
    """Get information about a word."""
    word = await repository.get_word(args.base_form)
    if not word:
        raise CLIError(f"Word '{args.base_form}' not found")

    print(f"Word: {word.base_form}")
    print(f"Declension class: {word.declension_class}")
    if word.gradation_type:
        print(f"Gradation: {word.gradation_type}")

    stems = await repository.get_stems(word)
    if stems:
        print("\nStems:")
        for stem_type, stem in stems.items():
            print(f"  {stem_type.value}: {stem}")


async def generate_form(
    generator: WordGenerator,
    base_form: str,
    case: str,
) -> None:
    """Generate a specific form of a word.

    Args:
        generator: Word form generator instance
        base_form: Base form of the word
        case: Case to generate
    """
    form = await generator.generate(base_form, Case(case))
    if not form:
        msg = f"Could not generate {case} form " f"for '{base_form}'"
        raise CLIError(msg)
    print(form)


async def run_command(args: argparse.Namespace) -> None:
    """Run the specified command."""
    if not args.command:
        create_parser().print_help()
        sys.exit(1)

    async with get_session() as session:
        repository = repo.SQLiteWordRepository(session)
        manager = WordFormManager(repository)
        generator = WordGenerator(repository)

        if args.command == "add-forms":
            await add_word_with_forms(manager, args)
        elif args.command == "add-stem":
            await add_word_stem(repository, args)
        elif args.command == "info":
            await get_word_info(repository, args)
        elif args.command == "gen":
            await generate_form(generator, args.base_form, args.case)


async def main() -> NoReturn:
    """Run the CLI application."""
    try:
        args = create_parser().parse_args()
        await run_command(args)
        sys.exit(0)
    except CLIError as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nOperation cancelled by user", file=sys.stderr)
        sys.exit(130)
    except (ValueError, TypeError) as e:
        print(f"Invalid input: {str(e)}", file=sys.stderr)
        sys.exit(1)
    except OSError as e:
        print(f"System error: {str(e)}", file=sys.stderr)
        sys.exit(2)
    except Exception as e:  # pylint: disable=broad-except
        err = f"{e.__class__.__name__}: {str(e)}"
        print(
            f"Unexpected error: {err}",
            file=sys.stderr,
        )
        sys.exit(2)


if __name__ == "__main__":
    asyncio.run(main())
