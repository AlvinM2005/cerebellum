from enum import Enum

class Result(Enum):
    # Define possible trial outcomes
    Correct = "Correct"
    Incorrect = "Incorrect"
    Timeout = "Timeout"