"""
This module defines the MonthHeaders class, a StrEnum containing the values of all the relevant
column headers within the month sheets
"""
from enum import StrEnum


class MonthHeaders(StrEnum):
    """
    The MonthHeaders class contains enummed values of all the relevant column headers within the
    month sheets
    """
    PERSONAL_NUM = "Osobní číslo"
    BIRTH_NUM = "Rodné číslo"
    CONTRACT_START = "Dat vstupu"
    CONTRACT_END = "Dat odchodu"
    GROSS_PAY = "Hrubá mzda"
    INSURANCE_PAYMENT = "součet soc + zdrav"
    PAY_FOR_ACTUAL_WORK = "Záklmzda"
