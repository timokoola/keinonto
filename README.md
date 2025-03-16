# Keinonto

A Python library for generating Finnish word forms from base forms to declinated forms.

## Overview

Keinonto is a specialized library that handles the complex task of Finnish word form generation. For example:
- Input: `sana` (word) + `plural, inessive`
- Output: `sanoissa` (in the words)

The library handles:
- 51 noun declination classes
- Multiple consonant gradation patterns
- Complex Finnish morphology rules
- Efficient backing database for word forms

## Features

- Generate correct Finnish word forms based on base form and target case
- Efficient and minimal database footprint
- Type-safe API design
- Command-line interface for quick testing and word management
- Extensible architecture for future additions (verbs, possessive forms, etc.)
- Comprehensive test suite using multiple word lists (Keinonto set, Kotus)

## Installation

```bash
pip install keinonto
```

### Development Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/keinonto.git
cd keinonto
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install development dependencies:
```bash
pip install -r requirements-dev.txt
```

4. Install Voikko library (required for testing):
```bash
# Ubuntu/Debian
sudo apt-get install libvoikko-dev

# macOS
brew install libvoikko

# Windows
# See https://voikko.puimula.org/windows.html
```

## Usage

### Python API

```python
from keinonto import WordGenerator

# Initialize the generator
generator = WordGenerator()

# Generate a word form
result = generator.generate(
    word="sana",
    case="inessive",
    number="plural"
)
print(result)  # Output: sanoissa

# Get all possible forms for a word
forms = generator.get_all_forms("sana")
```

### Command Line Interface

The library includes a CLI for quick testing and word management:

```bash
# Show available commands
python -m keinonto.cli --help

# Add a word with its forms from a JSON file
python -m keinonto.cli add-forms talo 1 forms.json

# Add a stem for a word
python -m keinonto.cli add-stem talo strong taloi

# Get information about a word
python -m keinonto.cli info talo

# Generate a specific form of a word
python -m keinonto.cli gen talo nominative
```

Example forms.json format:
```json
{
    "nominative_singular": "talo",
    "genitive_singular": "talon",
    "partitive_singular": "taloa",
    "nominative_plural": "talot",
    "inessive_singular": "talossa",
    "illative_singular": "taloon"
}
```

Required forms for word addition:
- nominative_singular (base form)
- genitive_singular (for weak stem)
- partitive_singular (for special stems)
- nominative_plural (for plural stem)
- inessive_singular (for locative cases)
- illative_singular (for special illative handling)

## Project Structure

```
keinonto/
├── domain/           # Core domain logic
│   ├── entities/     # Word forms, declination classes
│   ├── value_objects/# Cases, numbers, gradations
│   └── interfaces/   # Abstract interfaces
├── infrastructure/   # External implementations
│   ├── database/    # Word form database
│   └── external/    # External service integrations
└── presentation/    # Public API
    └── api/         # Main API endpoints
```

## Testing

The project uses pytest for testing. Tests are run in Docker containers to ensure consistent environment with Voikko library:

```bash
# Run all tests
docker-compose up test

# Run specific test file
docker-compose run test pytest tests/test_word_generator.py
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'feat: add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

Please ensure your PR:
- Follows the project's coding standards
- Includes appropriate tests
- Updates documentation as needed
- Passes all CI checks

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [Kotus](https://www.kotus.fi/) - Institute for the Languages of Finland
- [Voikko](https://voikko.puimula.org/) - Free linguistic software for Finnish
- Finnish language researchers and linguists who have documented the language rules

## Future Plans

- Support for verb conjugations
- Possessive form handling
- Compound word generation
- Extended word list coverage
- Performance optimizations
- Web API service
- Enhanced CLI functionality
  - Batch word import/export
  - Interactive word form editing
  - Form validation improvements

## Contact

For questions and support, please open an issue in the GitHub repository or contact the maintainers directly.
