"""Defines the mapper for translating insurance company names to their numbers."""
from types import MappingProxyType

from Enums import ErrNoEnum
from Utils.app_error import AppError


class InsuranceCompanyMapper:
    """Defines the mappings for translating insurance company names to their numbers."""

    _MAPPING: MappingProxyType[str, int] = MappingProxyType({
        "Všeobecná zdravotní pojišťovna ČR": 111,
        "VZP": 111,
        "Vojenská zdravotní pojišťovna ČR": 201,
        "VOZP": 201,
        "Česká průmyslová zdravotní pojišťovna": 205,
        "ČPZP": 205,
        "Oborová zdravotní pojišťovna zaměstnanců bank, pojišťoven a stavebnictví": 207,
        "OZP": 207,
        "Zaměstnanecká pojišťovna Škoda": 209,
        "ZPŠ": 209,
        "Zdravotní pojišťovna ministerstva vnitra ČR": 211,
        "ZPMV": 211,
        "ZPMVČR": 211,
        "RBP, zdravotní pojišťovna": 213,
        "Revírní bratrská pokladna, zdravotní pojišťovna": 213,
    })
    """
    Mapping attribute containing the mapping of strings to insurance company numbers, as assigned in CZE.
    :meta protected:
    """

    @classmethod
    def from_str(cls, value: str) -> int:
        """Convert insurance company name to its insurance company number.

        Converts the given string to an insurance company number
        :param value: string to convert to an insurance company number
        :return: int representing the company number
        :raises AppError: if an invalid string is passed
        """
        try:
            return cls._MAPPING[value]
        except KeyError as e:
            raise AppError(
                error_code=ErrNoEnum.INTERNAL_ERROR,
                error_message=f"Invalid insurance company name: {value}") from e
