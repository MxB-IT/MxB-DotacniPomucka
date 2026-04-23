"""Defines the mapper used to map a number to a disability type."""
from types import MappingProxyType

from src.Enums import ErrNoEnum
from src.Enums.disability_status_enum import DisabilityStatus
from src.Utils.app_error import AppError


class DisabilityTypeMapper:
    """Contains the mapping used to map a number to a disability type."""

    _MAPPING: MappingProxyType[int, DisabilityStatus] = MappingProxyType({
        1: DisabilityStatus.TZP,
        2: DisabilityStatus.TZP,
        3: DisabilityStatus.OZP12,
        4: DisabilityStatus.OZP12,
        5: DisabilityStatus.OZZ,
    })

    @classmethod
    def from_int(cls, value: int) -> DisabilityStatus:
        """Convert integer value to a disability status.

        Converts the given integer value to a disability status.
        :param value: Integer value to convert.
        :return: Disability status corresponding to the given integer value.
        :raises AppError: If an invalid integer value is passed.
        """
        try:
            return cls._MAPPING[value]
        except KeyError as e:
            raise AppError(
                error_code=ErrNoEnum.INTERNAL_ERROR,
                error_message=f"Invalid disability number: {value}.",
            ) from e
