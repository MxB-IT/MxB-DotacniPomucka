"""Defines an enum containing headers found in the HR sheet."""

from enum import StrEnum


class HumanResourcesHeaders(StrEnum):
    """Contains headers found in the HR sheet."""

    SURNAME = "Příjmení"
    FIRST_NAME = "Jméno"
    PERSONAL_NUM = "Osobní číslo"
    INSURANCE_COMPANY = "Pojišťovna"
    DISABILITY_STATUS = "Druh důchodu"
    DISABILITY_START = "Důchod pobírán od"
