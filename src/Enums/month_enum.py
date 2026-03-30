"""
This module defines an enum with all the czech month names, this is needed, because the Excel
sheets the application will be working with both contain exclusively Czech text
"""
from enum import StrEnum


class MonthEnum(StrEnum):
    """
    Contains a mapping of sorts for translating English month names into Czech
    """
    JAN = "LEDEN"
    FEB = "ÚNOR"
    MAR = "BŘEZEN"
    APR = "DUBEN"
    MAY = "KVĚTEN"
    JUN = "ČERVEN"
    JUL = "ČERVENEC"
    AUG = "SRPEN"
    SEP = "ZÁŘÍ"
    OCT = "ŘÍJEN"
    NOV = "LISTOPAD"
    DEC = "PROSINEC"
