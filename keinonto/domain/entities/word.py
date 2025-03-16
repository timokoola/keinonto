"""
Word entity representing a Finnish word and its properties.
"""

from typing import Optional
from pydantic import BaseModel, Field

from ..value_objects.case import Case
from ..value_objects.number import Number


class Word(BaseModel):
    """A Finnish word with its base form and properties."""
    
    base_form: str = Field(..., description="The dictionary form (nominative singular)")
    declension_class: int = Field(..., ge=1, le=51, description="Noun declension class (1-51)")
    gradation_type: Optional[str] = Field(None, description="Consonant gradation pattern if applicable")
    
    class Config:
        """Pydantic model configuration."""
        frozen = True  # Make instances immutable 