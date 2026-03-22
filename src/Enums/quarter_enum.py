"""
This module defines the quarters class, which contains a definition of the quarters of the year
(AKA, months represented by numbers presented as individual quarters of the year)
"""
from enum import Enum


class Quarters(Enum):
    """
    The Quarters class contains months encoded into their respective quarters based on their selectors
    """
    FIRST_QUARTER = (1, 2, 3)
    SECOND_QUARTER = (4, 5, 6)
    THIRD_QUARTER = (7, 8, 9)
    FOURTH_QUARTER = (10, 11, 12)
