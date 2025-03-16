"""Word entity module."""

from typing import List, Optional

from pydantic import BaseModel, Field

from ..value_objects.stem_type import StemType


class WordStem(BaseModel):
    """Word stem model."""

    stem_type: StemType
    value: str


class Word(BaseModel):
    """Word model."""

    base_form: str
    declension_class: int = Field(
        ...,
        ge=1,
        le=51,
        description="Noun declension class (1-51)",
    )
    gradation_type: Optional[str] = Field(
        None,
        description="Consonant gradation pattern if applicable",
    )
    stems: List[WordStem] = []

    class Config:
        """Pydantic model configuration."""

        frozen = True  # Make instances immutable
