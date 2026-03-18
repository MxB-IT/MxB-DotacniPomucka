"""
This module defines the Employee class used mainly as a data structure to put together data about
a certain employee before writing it into the government template
"""
from openpyxl.descriptors import DateTime

from src.Enums import ErrNoEnum
from src.Enums.disability_status_enum import DisabilityStatus
from src.Utils import ErrorHandler


class Employee:
    """
    The Employee class serves mainly as a data structure used to collect data about an employee
    before it is written into the government Excel template
    """
    def __init__(self):
        self._surname: str | None = None
        self._first_name: str | None = None
        self._birth_num: str | None = None
        self._date_of_contract_start: DateTime | None = None
        self._date_of_contract_end: DateTime | None = None
        self._insurance_code: int | None = None
        self._disability_recognised_from: DateTime | None = None
        self._disability_recognised_to: DateTime | None = None
        self._disability_status: DisabilityStatus | None = None
        self._pay: float | None = None
        self._insurance_payment: float | None = None

    def set_surname(self, surname: str) -> None:
        """
        setter for the surname private attribute
        :param surname: surname of the employee to save in the Employee instance
        :return: None
        """
        self._surname = surname

    def get_surname(self) -> str | None:
        """
        Getter for the surname private attribute, checks whether surname is blank and shows an
        error to the user if it is, to ensure the user knows why the writing failed
        :return:
        """
        if self._surname is None:
            ErrorHandler(error_message="Chyba během zpracování Excelu, zkontrolujte, že každý "
                                       "zaměstnanec má na vstupu zadané příjmení a zkuste to "
                                       "prosím znovu.",
                         error_code=ErrNoEnum.ERR_EMPLOYEE_MANDATORY_ATTR_NOT_SET)
            return None
        return self._surname


