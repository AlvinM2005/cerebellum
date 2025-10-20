# src/utils/enums.py
from enum import Enum

class Answer(Enum):
    """Possible participant answers in the task."""
    LONGER_LOUDER = "longer / louder"
    SHORTER_QUIETER = "shorter / quieter"