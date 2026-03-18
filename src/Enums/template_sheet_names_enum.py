"""
This module contains the enum for sheet names in the government Excel template, doing it like this,
so I don't have to type them out whenever I actually need them
"""
from enum import StrEnum


class TemplateSheetNames(StrEnum):
    """
    This class serves as an enum with the sheet names in the government Excel template encoded
    within it to nesure I do not make a typo anywhere
    """
    INTRO_SHEET = "1) Úvodní list"
    EMPLOYEE_LIST = "2) seznam zaměstnanců OZP"
    PROV_ASSISTANCE = "3) nákl. prov. asistence"
    TRANSPORTATION_COSTS = "4) nákl. na dopr."
    COSTS_ASSOCIATED_WITH_PROCESSING = "5) nákl. na přiz. prov."
    ADDITIONS_LIST = "6) seznam dokl."
    WARNING = "7) Upozornění"
