"""
This module contains the IntMonthMapper class, containing the mappings from ints to months in the
MonthEnum, allowing me to easily transform an intrger into a MonthEnum value
"""
from types import MappingProxyType

from src.Enums import MonthEnum


class IntMonthMapper:
    """
    The IntMonthMapper class handles mapping ints to MonthEnum values
    """
    _MAPPING = MappingProxyType({
        1: MonthEnum.JAN,
        2: MonthEnum.FEB,
        3: MonthEnum.MAR,
        4: MonthEnum.APR,
        5: MonthEnum.MAY,
        6: MonthEnum.JUN,
        7: MonthEnum.JUL,
        8: MonthEnum.AUG,
        9: MonthEnum.SEP,
        10: MonthEnum.OCT,
        11: MonthEnum.NOV,
        12: MonthEnum.DEC,
    })

    @classmethod
    def from_int(cls, value: int) -> MonthEnum:
        """
        Converts an integer to a MonthEnum value, raises ValueError if invalid
        :param value: integer to convert into a MonthEnum
        :return: MonthEnum
        :raises ValueError: if an invalid month number is passed
        """
        try:
            return cls._MAPPING[value]
        except KeyError as e:
            raise ValueError(f"Invalid month number: {value}") from e
