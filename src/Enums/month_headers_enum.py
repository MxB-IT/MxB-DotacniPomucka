"""Defines an enum containing all the headers found in the month sheets."""
from enum import StrEnum


class MonthHeaders(StrEnum):
    """Contains all the relevant headers found in the month sheet."""

    PERSONAL_NUM = "Osobní číslo"
    BIRTH_NUM = "Rodné číslo"
    CONTRACT_START = "Dat vstupu"
    CONTRACT_END = "Dat odchodu"
    GROSS_PAY = "Hrubá mzda"
    COMPANY_SOCIAL_SEC = "Socfirma"
    COMPANY_INSURANCE = "Zdrfirma"
    PAY_FOR_ACTUAL_WORK = "Záklmzda"
