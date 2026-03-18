"""
This module defines the enumertaion of all the possible disability statuses that the government
Excel template accepts
"""

from enum import StrEnum


class DisabilityStatus(StrEnum):
    """
    This class contains the enumeration of all the possible disability statuses that the government
    Excel template recognises
    """
    TZP = "TZP",
    OZP12 = "OZP12"
    OZZ = "OZZ"
