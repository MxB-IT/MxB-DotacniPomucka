"""Defines the enum containing all disability statuses."""

from enum import StrEnum


class DisabilityStatus(StrEnum):
    """Contains the enumeration of all the disability statuses used in the app."""

    TZP = "TZP"
    OZP12 = "OZP12"
    OZZ = "OZZ"
