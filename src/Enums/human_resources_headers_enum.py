"""
This module defines the HumanResourcesHeaders class containing the header values of all the
relevant columns in the human resources sheet
"""

from enum import StrEnum


class HumanResourcesHeaders(StrEnum):
    """
    The HumanResourcesHeaders class contains the header values of all the relevant columns in the
    human resources sheet
    """
    SURNAME = "Příjmení"
    FIRST_NAME = "Jméno"
    PERSONAL_NUM = "Osobní číslo"
    INSURANCE_COMPANY = "Pojišťovna"
    DISABILITY_STATUS = "Druh důchodu"
    DISABILITY_START = "Důchod pobírán od"
