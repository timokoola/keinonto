"""
Grammatical number (singular/plural) as value objects.
"""

from enum import Enum


class Number(str, Enum):
    """Grammatical number in Finnish."""
    
    SINGULAR = "singular"  # yksikkö
    PLURAL = "plural"      # monikko 