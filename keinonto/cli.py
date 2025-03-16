"""Command line interface for quick testing."""

import argparse
import asyncio
import sys
from typing import NoReturn, Optional

from keinonto.domain.entities.word import Word
from keinonto.domain.value_objects.case import Case
from keinonto.domain.value_objects.stem_type import StemType
from keinonto.infrastructure.database.config import get_session
from keinonto.infrastructure.database import sqlite_repository as repo
from keinonto.presentation.api.word_generator import WordGenerator


class CLIError(Exception):
    """Base class for CLI errors."""


def stem_type_arg(value: str) -> str:
    """Convert stem type argument to proper format."""
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


async def add_word(
    repository: repo.SQLiteWordRepository,
    base_form: str,
    declension_class: int,
    gradation_type: Optional[str] = None,
) -> None:
    """Add a new word to the repository."""
    try:
        word = Word(
            base_form=base_form,
            declension_class=declension_class,
            gradation_type=gradation_type,
        )
        await repository.save_word(word)
        print(f"Added word: {base_form}")
    except (ValueError, KeyError) as e:
        print(f"Invalid word data: {str(e)}")
        raise CLIError from e
    except Exception as e:
        print(f"Database error: {str(e)}")
        raise CLIError from e


async def add_stem(
    repository: repo.SQLiteWordRepository,
    base_form: str,
    stem_type: str,
    stem: str,
) -> None:
    """Add a stem to an existing word."""
    try:
        word = await repository.get_word(base_form)
        if not word:
            print(f"Word not found: {base_form}")
            raise CLIError("Word not found")

        await repository.save_stem(word, StemType(stem_type), stem)
        msg = f"Added {stem_type} stem '{stem}' to word '{base_form}'"
        print(msg)
    except (ValueError, KeyError) as e:
        print(f"Invalid stem data: {str(e)}")
        raise CLIError from e
    except Exception as e:
        print(f"Database error: {str(e)}")
        raise CLIError from e


async def get_word_info(
    repository: repo.SQLiteWordRepository,
    base_form: str,
) -> None:
    """Show information about a word."""
    try:
        word = await repository.get_word(base_form)
        if not word:
            print(f"Word not found: {base_form}")
            raise CLIError("Word not found")

        print(f"\nWord: {word.base_form}")
        print(f"Declension class: {word.declension_class}")
        if word.gradation_type:
            print(f"Gradation type: {word.gradation_type}")
        print("\nStems:")
        if word.stems:
            for stem in word.stems:
                print(f"  {stem.stem_type.value}: {stem.value}")
        else:
            print("  No stems defined")
    except Exception as e:
        print(f"Error retrieving word: {str(e)}")
        raise CLIError from e


async def generate_form(
    generator: WordGenerator,
    base_form: str,
    case: str,
) -> None:
    """Generate a specific form of a word."""
    try:
        form = await generator.generate(base_form, case.lower())
        if form:
            print(f"\n{base_form} ({case}): {form}")
        else:
            msg = f"\nCould not generate {case} form for '{base_form}'"
            print(msg)
            raise CLIError(msg)
    except (ValueError, KeyError) as e:
        print(f"Invalid word or case: {str(e)}")
        raise CLIError from e
    except Exception as e:
        print(f"Generation error: {str(e)}")
        raise CLIError from e


def create_parser() -> argparse.ArgumentParser:
    """Create and configure the argument parser."""
    parser = argparse.ArgumentParser(
        description="Finnish word form generation tool"
    )
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Add word command
    add_parser = subparsers.add_parser("add", help="Add a new word")
    add_parser.add_argument("base_form", help="Base form of the word")
    add_parser.add_argument(
        "declension_class",
        type=int,
        help="Declension class (1-51)",
    )
    add_parser.add_argument(
        "--gradation",
        help="Gradation type (e.g., 't-d')",
    )

    # Add stem command
    stem_parser = subparsers.add_parser("stem", help="Add a stem to a word")
    stem_parser.add_argument("base_form", help="Base form of the word")
    stem_parser.add_argument(
        "stem_type",
        type=stem_type_arg,
        help=f"Type of stem. Types: {', '.join(t.value for t in StemType)}",
    )
    stem_parser.add_argument("stem", help="The stem form")

    # Get word info command
    info_parser = subparsers.add_parser("info", help="Get word information")
    info_parser.add_argument("base_form", help="Base form of the word")

    # Generate form command
    gen_parser = subparsers.add_parser("gen", help="Generate word form")
    gen_parser.add_argument("base_form", help="Base form of the word")
    gen_parser.add_argument(
        "case",
        type=case_type,
        help=f"Case to generate. Cases: {', '.join(c.value for c in Case)}",
    )

    return parser


async def main() -> NoReturn:
    """Run the CLI application."""
    parser = create_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    try:
        async with get_session() as session:
            repository = repo.SQLiteWordRepository(session)
            generator = WordGenerator(repository)

            if args.command == "add":
                await add_word(
                    repository,
                    args.base_form,
                    args.declension_class,
                    args.gradation,
                )
            elif args.command == "stem":
                await add_stem(
                    repository,
                    args.base_form,
                    args.stem_type,
                    args.stem,
                )
            elif args.command == "info":
                await get_word_info(repository, args.base_form)
            elif args.command == "gen":
                await generate_form(generator, args.base_form, args.case)
    except CLIError:
        sys.exit(1)
    except Exception as e:
        print(f"\nUnexpected error: {str(e)}")
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    asyncio.run(main())
