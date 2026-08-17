"""Defines an enum containing tuples with numbers representing the months within each quarter."""
from enum import Enum


class Quarters(Enum):
    """Contains tuples with numbers representing the months within each quarter of the year."""

    FIRST_QUARTER = (1, 2, 3)
    SECOND_QUARTER = (4, 5, 6)
    THIRD_QUARTER = (7, 8, 9)
    FOURTH_QUARTER = (10, 11, 12)
