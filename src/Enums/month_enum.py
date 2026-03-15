"""
This module defines an enum with all the czech month names, this is needed, because the Excel
sheets the application will be working with both contain exclusively Czech text
"""
from enum import StrEnum


class MonthEnum(StrEnum):
    """
    Contains a mapping of sorts for translating English month names into Czech
    """
    JAN = "Leden",
    FEB = "Únor",
    MAR = "Březen",
    APR = "Duben",
    MAY = "Květen",
    JUN = "Červen",
    JUL = "Červenec",
    AUG = "Srpen",
    SEP = "Září",
    OCT = "Říjen"
    NOV = "Listopad",
    DEC = "Prosinec"