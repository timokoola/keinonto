"""Value object for different stem types."""

from enum import Enum


class StemType(str, Enum):
    """Enumeration of different stem types used in word inflection."""

    STRONG = "strong"  # Strong stem, used in nominative singular
    WEAK = "weak"  # Weak stem, used in some inflected forms
    PLURAL = "plural"  # Plural stem, used in plural forms
    ILLATIVE = "illative"  # Special stem for illative case
    GENITIVE = "genitive"  # Special stem for genitive/partitive
