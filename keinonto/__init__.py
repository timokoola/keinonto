"""
Keinonto - Finnish Word Form Generation Library
"""

from importlib import metadata

from .presentation.api.word_generator import WordGenerator

__version__ = metadata.version("keinonto")

__all__ = ["WordGenerator"] 