"""Defines an enum containing the names of all sheets found in the template."""
from enum import StrEnum


class TemplateSheetNames(StrEnum):
    """Contains the names of all sheets found in the template."""

    INTRO_SHEET = "1) Úvodní list"
    EMPLOYEE_LIST = "2) seznam zaměstnanců OZP"
    PROV_ASSISTANCE = "3) nákl. prov. asistence"
    TRANSPORTATION_COSTS = "4) nákl. na dopr."
    COSTS_ASSOCIATED_WITH_PROCESSING = "5) nákl. na přiz. prov."
    ADDITIONS_LIST = "6) seznam dokl."
    WARNING = "7) Upozornění"
