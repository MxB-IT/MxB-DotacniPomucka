"""Defines an enum containing month names in Czech."""
from enum import StrEnum


class MonthEnum(StrEnum):
    """Contains a mapping of sorts for translating English month names into Czech."""

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
