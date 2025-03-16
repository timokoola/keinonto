"""Performance tests for keinonto library."""

import asyncio
import json
import time
from typing import Any, Dict, List, Optional, Tuple

import jsonlines
import pytest
import pytest_asyncio
from rich import print as rich_print
from rich.console import Console
from rich.table import Table
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
)
from sqlalchemy.orm import sessionmaker
from voikko import libvoikko

from keinonto.infrastructure.database.sqlite_repository import (
    SQLiteWordRepository,
)
from keinonto.presentation.api.word_generator import WordGenerator

ResultsDict = Dict[
    Tuple[str, Optional[str]], Dict[str, List[Dict[str, Any]]]
]
TestForm = Dict[str, Any]


def load_test_data(sample_size: int = 100) -> List[Dict[str, Any]]:
    """Load test data from the extracted dataset."""
    data = []

    # Read from the extracted jsonl file
    with jsonlines.open('keinonto-dataset/keinonto-dataset.jsonl') as reader:
        for obj in reader:
            data.append(obj)

    # Ensure unique combinations of case and class
    seen = set()
    unique_data = []
    for item in data:
        key = (item['sijamuoto'], item.get('class', ''))
        if key not in seen:
            seen.add(key)
            unique_data.append(item)
            if len(unique_data) >= sample_size:
                break

    # If we don't have enough unique combinations, just return what we have
    return unique_data[:sample_size]


async def run_performance_test(
    word_generator: WordGenerator,
    test_data: List[Dict[str, Any]],
    voikko: libvoikko.Voikko,
) -> Tuple[List[Dict[str, Any]], Dict[str, int]]:
    """Run performance test on word generation."""
    results = []
    stats = {'total': 0, 'success': 0, 'error': 0}

    # Print all unique case names
    unique_cases = {item['sijamuoto'].lower() for item in test_data}
    rich_print("\nUnique case names in test data:")
    for case in sorted(unique_cases):
        rich_print(f"- {case}")

    # Print all unique number values
    unique_numbers = {str(item.get('number', '')) for item in test_data}
    rich_print("\nUnique number values in test data:")
    for number in sorted(unique_numbers):
        rich_print(f"- {number}")

    for item in test_data:
        stats['total'] += 1
        try:
            # Get number value, default to 'singular' if empty
            number = item.get('number', '')
            if not number:
                number = 'singular'
            elif number not in ['singular', 'plural']:
                rich_print(
                    f"Warning: Invalid number value '{number}', skipping"
                )
                continue

            # Generate word
            word = await word_generator.generate(
                item['word'],
                item['sijamuoto'],
                number,
            )

            # Validate with Voikko and print details
            rich_print(f"\nProcessing word: {item['word']}")
            rich_print(f"Case: {item['sijamuoto']}, Number: {number}")
            rich_print(f"Generated form: {word}")
            analysis = voikko.analyze(word)
            is_valid = len(analysis) > 0
            if is_valid:
                rich_print(
                    "Voikko analysis:",
                    json.dumps(analysis[0], indent=2, ensure_ascii=False),
                )
            else:
                rich_print("Voikko analysis: No valid analysis found")

            result = {
                'input': item['word'],
                'case': item['sijamuoto'],
                'number': item['number'],
                'class': item.get('class', ''),
                'output': word,
                'valid': is_valid,
            }

            if is_valid:
                stats['success'] += 1
            else:
                stats['error'] += 1

            results.append(result)

        except Exception as exc:  # pylint: disable=broad-except
            stats['error'] += 1
            rich_print(f"\nError processing word {item['word']}: {str(exc)}")
            results.append({
                'input': item['word'],
                'case': item['sijamuoto'],
                'number': item['number'],
                'class': item.get('class', ''),
                'output': None,
                'error': str(exc),
            })

    return results, stats


def print_results(results: List[Dict[str, Any]], stats: Dict[str, int]) -> None:
    """Print test results in a formatted table."""
    console = Console()

    # Print summary statistics
    console.print("\n[bold]Performance Test Results[/bold]")
    console.print(f"Total tests: {stats['total']}")
    console.print(f"Successful: {stats['success']}")
    console.print(f"Failed: {stats['error']}")
    success_rate = (stats['success'] / stats['total']) * 100
    console.print(f"Success rate: {success_rate:.2f}%\n")

    # Create results table
    table = Table(show_header=True, header_style="bold")
    table.add_column("Input")
    table.add_column("Case")
    table.add_column("Number")
    table.add_column("Class")
    table.add_column("Output")
    table.add_column("Valid")

    for result in results:
        table.add_row(
            result['input'],
            result['case'],
            result['number'],
            result['class'],
            result.get('output', 'ERROR'),
            str(result.get('valid', False)),
        )

    console.print(table)


@pytest_asyncio.fixture(scope="function")
async def generator_fixture():
    """Create a WordGenerator instance for testing."""
    engine = create_async_engine("sqlite+aiosqlite:///keinonto.db")
    async_session = sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with async_session() as session:
        repository = SQLiteWordRepository(session)
        generator = WordGenerator(repository)
        yield generator


@pytest.mark.benchmark(
    group="word_generation",
    min_rounds=5,
    timer=time.time,
    disable_gc=True,
    warmup=False,
)
def test_word_generation(benchmark, generator_fixture):
    """Run performance test for word generation."""
    # Load test data
    test_data = load_test_data()

    async def run_test():
        """Run the performance test."""
        results = []

        # Print all unique case names
        unique_cases = {item['sijamuoto'].lower() for item in test_data}
        rich_print("\nUnique case names in test data:")
        for case in sorted(unique_cases):
            rich_print(f"- {case}")

        # Print all unique number values
        unique_numbers = {str(item.get('number', '')) for item in test_data}
        rich_print("\nUnique number values in test data:")
        for number in sorted(unique_numbers):
            rich_print(f"- {number}")

        for item in test_data:
            word = item['word']
            case = item['sijamuoto'].lower()
            number = item['number']

            # Map Finnish case names to English
            case_mapping = {
                'nimento': 'nominative',
                'omanto': 'genitive',
                'osanto': 'partitive',
                'olento': 'essive',
                'tulento': 'translative',
                'sisaolento': 'inessive',
                'sisaeronto': 'elative',
                'sisatulento': 'illative',
                'ulkoolento': 'adessive',
                'ulkoeronto': 'ablative',
                'ulkotulento': 'allative',
                'vajanto': 'abessive',
                'keinonto': 'instructive',
                'seuranto': 'comitative',
                # Handle empty case name
                '': 'nominative',  # Default to nominative for empty case
                # Handle kerrontosti case
                'kerrontosti': 'instructive',  # Based on -sti suffix
            }

            try:
                # Convert Finnish case name to English
                case = case_mapping.get(case)
                if not case:
                    rich_print(f"Warning: Unknown case {item['sijamuoto']}")
                    continue

                result = await generator_fixture.generate(
                    word=word,
                    case=case,
                    number=number,
                )
                results.append(result)
            except Exception as exc:  # pylint: disable=broad-except
                rich_print(f"Error processing word {word}: {str(exc)}")

        return results

    def run_single_test():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(run_test())
        finally:
            loop.close()
            asyncio.set_event_loop(None)

    # Run the benchmark
    results = benchmark(run_single_test)

    # Validate results
    assert len(results) > 0, "No results were generated"
    success_count = sum(1 for result in results if result is not None)
    success_rate = success_count / len(results) * 100
    rich_print(f"Success rate: {success_rate:.2f}%")
    assert success_rate > 80, f"Success rate {success_rate:.2f}% is below 80%"


async def main():
    """Run performance tests."""
    # Initialize Voikko
    voikko = libvoikko.Voikko("fi")

    # Load test data
    test_data = load_test_data()

    # Initialize database connection
    engine = create_async_engine("sqlite+aiosqlite:///keinonto.db")
    async_session = sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with async_session() as session:
        # Initialize word generator
        repository = SQLiteWordRepository(session)
        generator = WordGenerator(repository)

        # Run performance test
        results, stats = await run_performance_test(generator, test_data, voikko)

        # Print results
        print_results(results, stats)


if __name__ == "__main__":
    asyncio.run(main())
