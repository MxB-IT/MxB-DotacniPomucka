"""Defines a mapper that maps numbers to month enum values."""
from types import MappingProxyType

from src.Enums import ErrNoEnum, MonthEnum
from src.Utils.app_error import AppError


class IntMonthMapper:
    """Contains a mapping, allowing numbers to be mapped to month enum values."""

    _MAPPING: MappingProxyType[int, MonthEnum] = MappingProxyType({
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
        """Get a month enum value from the given integer value.

        Converts an integer to a MonthEnum value, raises ValueError if invalid
        :param value: integer to convert into a MonthEnum
        :return: MonthEnum
        :raises ValueError: if an invalid month number is passed
        """
        try:
            return cls._MAPPING[value]
        except KeyError as e:
            raise AppError(
                error_code=ErrNoEnum.INTERNAL_ERROR,
                error_message=f"Invalid month number: {value}") from e
