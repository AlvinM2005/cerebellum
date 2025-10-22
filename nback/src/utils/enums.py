# src/utils/enums.py
from enum import Enum

class Answer(Enum):
    """Possible participant answers in the task."""
    SAME = "same"
    DIFFERENT = "different"
    NOGO = "nogo"