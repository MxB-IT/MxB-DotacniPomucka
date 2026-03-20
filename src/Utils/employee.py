"""
This module defines the Employee class used mainly as a data structure to put together data about
a certain employee before writing it into the government template
"""
from openpyxl.descriptors import DateTime

from src.Enums import ErrNoEnum, MonthEnum
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
        self._contract_start_date: DateTime | None = None
        self._contract_end_date: DateTime | None = None
        self._insurance_code: int | None = None
        self._disability_recognised_from: DateTime | None = None
        self._disability_recognised_to: DateTime | None = None
        self._disability_status: DisabilityStatus | None = None
        self._pay: dict[MonthEnum, float] | None = None
        self._insurance_payment: dict[MonthEnum, float] | None = None

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
        :return: surname of the employee if it exists, None otherwise
        """
        if self._surname is None:
            ErrorHandler(error_message="Chyba během zpracování Excelu, zkontrolujte, že každý "
                                       "zaměstnanec má na vstupu zadané příjmení a zkuste to "
                                       "prosím znovu.",
                         error_code=ErrNoEnum.ERR_EMPLOYEE_MANDATORY_ATTR_NOT_SET)
        return self._surname

    def get_first_name(self) -> str:
        """
        Getter for the first name private attribute, checks whether first name is blank and shows
        an error to the user if it is, to ensure the user knows why the writing failed
        :return: first name of the employee if it exists, None otherwise
        """
        if self._first_name is None:
            ErrorHandler(
                error_message="Chyba během zpracování Excelu, zkontrolujte, že každý "
                "zaměstnanec má na vstupu zadané křestní jméno a zkuste to "
                "prosím znovu.",
                error_code=ErrNoEnum.ERR_EMPLOYEE_MANDATORY_ATTR_NOT_SET,
            )
        return self._first_name

    def set_first_name(self, first_name: str) -> None:
        """
        Setter for the first_name private attribute
        :param first_name: first_name to assign to the employee instance
        :return: None
        """
        self._first_name = first_name

    def set_birth_num(self, birth_num: str) -> None:
        """
        Setter for the birth_num private attribute
        :param birth_num: birth_num to assign to the employee instance
        :return: None
        """
        self._birth_num = birth_num

    def get_birth_num(self) -> str | None:
        """
        Getter for the birth number private attribute, since birth num can be blank (with
        foreigners for example), it is not checked for blankness
        :return: birth number of the employee if it exists, None otherwise
        """
        return self._birth_num

    def set_contract_start_date(self, contract_start_date: DateTime) -> None:
        """
        Setter for the date_of_contract_start private attribute
        :param contract_start_date: date of contrast start to assign to the employee instance
        :return: None
        """
        self._contract_start_date = contract_start_date

    def get_contract_start_date(self) -> DateTime | None:
        """
        Getter for the contract start date private attribute, checks whether contract start date
        is blank and shows an error to the user if it is, to ensure the user knows why the writing
        failed
        :return: contract start date for the employee if it exists, None otherwise
        """
        if self._contract_start_date is None:
            ErrorHandler(
                error_message="Chyba během zpracování Excelu, zkontrolujte, že každý "
                "zaměstnanec má na vstupu zadané datum vzniku pracovního poměru a zkuste to "
                "prosím znovu.",
                error_code=ErrNoEnum.ERR_EMPLOYEE_MANDATORY_ATTR_NOT_SET,
            )
        return self._contract_start_date

    def set_contract_end_date(self, contract_end_date: DateTime) -> None:
        """
        Setter for the contract end date private attribute
        :param contract_end_date: contract end date to assign to the employee instance
        :return: None
        """
        self._contract_end_date = contract_end_date

    def get_contract_end_date(self) -> DateTime | None:
        """
        Getter for the contract end date private attribute, since this information is not mandatory
        to fill in, this getter does not error when the attribute is None
        :return: contract end date for the employee if it exists, None otherwise
        """
        return self._contract_end_date

    def set_insurance_code(self, insurance_code: int) -> None:
        """
        Setter for the insurance code private attribute
        :param insurance_code: insurance code to assign to the employee instance
        :return: None
        """
        self._insurance_code = insurance_code

    def get_insurance_code(self) -> int | None:
        """
        Getter for the insurance code private attribute, checks whether insurance code is blank and
        shows an error to the user if it is, to ensure the user knows why the writing failed
        :return: insurance code for the employee if it exists, None otherwise
        """
        if self._insurance_code is None:
            ErrorHandler(
                error_message="Chyba během zpracování Excelu, zkontrolujte, že každý "
                "zaměstnanec má na vstupu zadané číslo pojišťovny a zkuste to "
                "prosím znovu.",
                error_code=ErrNoEnum.ERR_EMPLOYEE_MANDATORY_ATTR_NOT_SET,
            )
        return self._insurance_code

    def set_disability_recognised_from(self, disability_recognised_from: DateTime) -> None:
        """
        Setter for the private attribute signifying from when the employees disability is
        officially recognised
        :param disability_recognised_from: DateTime representation of from what date the employees
        disability is officially recognised from
        :return: None
        """
        self._disability_recognised_from = disability_recognised_from

    def get_disability_recognised_from(self) -> DateTime | None:
        """
        Getter for the disability recognised from private attribute, checks whether disability
        recognised from is blank and shows an error to the user if it is, to ensure the user knows
        why the writing failed
        :return: disability recognised from for the employee if it exists, None otherwise
        """
        if self._disability_recognised_from is None:
            ErrorHandler(
                error_message="Chyba během zpracování Excelu, zkontrolujte, že každý "
                "zaměstnanec má na vstupu zadané odkdy je mu uznávána invalidita a zkuste to "
                "prosím znovu.",
                error_code=ErrNoEnum.ERR_EMPLOYEE_MANDATORY_ATTR_NOT_SET,
            )
        return self._disability_recognised_from

    def set_disability_recognised_to(self, disability_recognised_to: DateTime) -> None:
        """
        Setter for the private attribute signifying until which date the employees disability is
        officially recognised
        :param disability_recognised_to: DateTime representation of until which date the employees
        disability is officially recognised from
        :return: None
        """
        self._disability_recognised_to = disability_recognised_to

    def get_disability_recognised_to(self) -> DateTime | None:
        """
        Getter for the disability recognised to private attribute, since this information is not
        mandatory to fill in, this getter does not error when the attribute is None
        :return: disability recognised to for the employee if it exists, None otherwise
        """
        return self._disability_recognised_to

    def set_disability_status(self, disability_status: DisabilityStatus) -> None:
        """
        Setter for the disability status private attribute
        :param disability_status: disability status to assign to the employee instance
        :return: None
        """
        self._disability_status = disability_status

    def get_disability_status(self) -> DisabilityStatus | None:
        """
        Getter for the disability status private attribute, checks whether disability status is
        blank and shows an error to the user if it is, to ensure the user knows why the writing
        failed
        :return: disability status for the employee if it exists, None otherwise
        """
        if self._disability_status is None:
            ErrorHandler(
                error_message="Chyba během zpracování Excelu, zkontrolujte, že každý "
                "zaměstnanec má na vstupu zadaný status invalidity a zkuste to "
                "prosím znovu.",
                error_code=ErrNoEnum.ERR_EMPLOYEE_MANDATORY_ATTR_NOT_SET,
            )
        return self._disability_status

    def set_pay(self, month: MonthEnum, pay: float) -> None:
        """
        Setter for the pay private attribute, sets pay for the chosen month
        :param month: month for which the salary is relevant
        :param pay: the employee's salary before tax
        :return: None
        """
        self._pay[month] = pay

    def get_pay(self, month: MonthEnum) -> float | None:
        """
        Getter for the pay for a given month private attribute, checks whether pay for the month is
        blank and shows an error to the user if it is, to ensure the user knows why the writing
        failed
        :param month: month from which to get the employee's pay
        :return: pay for a given month for the employee if it exists, None otherwise
        """
        try:
            if self._pay[month] is None:
                ErrorHandler(
                    error_message="Chyba během zpracování Excelu, zkontrolujte, že každý "
                                  "zaměstnanec má na vstupu zadanou pro každý měsíc hrubou mzdu a "
                                  "zkuste to prosím znovu.",
                    error_code=ErrNoEnum.ERR_EMPLOYEE_MANDATORY_ATTR_NOT_SET,
                )
            return self._pay[month]
        except KeyError:
            ErrorHandler(
                error_message="Chyba během zpracování Excelu, zkontrolujte, že každý "
                "zaměstnanec má na vstupu zadanou pro každý měsíc hrubou mzdu a "
                "zkuste to prosím znovu.",
                error_code=ErrNoEnum.ERR_EMPLOYEE_MANDATORY_ATTR_NOT_SET,
            )
            return None

    def set_insurance_payment(self, month: MonthEnum, insurance_payment: float) -> None:
        """
        Setter for the insurance payment private attribute, sets insurance payment for the chosen
        month
        :param month: month for which to set the amount of insurance payment provided by the
        employer
        :param insurance_payment: amount of money paid
        :return: None
        """
        self._insurance_payment[month] = insurance_payment

    def get_insurance_payment(self, month: MonthEnum) -> float | None:
        """
        Getter for the insurance payment for a given month private attribute, checks whether
        insurance payment for the month is blank and shows an error to the user if it is, to ensure
        the user knows why the writing failed
        :param month: month from which to get the amount of insurance payment provided by the
        employer
        :return: insurance payment for a given month provided bny the employer if it exists, None
        otherwise
        """
        try:
            if self._insurance_payment[month] is None:
                ErrorHandler(
                    error_message="Chyba během zpracování Excelu, zkontrolujte, že každý "
                                  "zaměstnanec má na vstupu zadán pro každý měsíc odvod pojistného"
                                  " a zkuste to prosím znovu.",
                    error_code=ErrNoEnum.ERR_EMPLOYEE_MANDATORY_ATTR_NOT_SET,
                )
            return self._insurance_payment[month]
        except KeyError:
            ErrorHandler(
                error_message="Chyba během zpracování Excelu, zkontrolujte, že každý "
                "zaměstnanec má na vstupu zadán pro každý měsíc odvod pojistného "
                "a zkuste to prosím znovu.",
                error_code=ErrNoEnum.ERR_EMPLOYEE_MANDATORY_ATTR_NOT_SET,
            )
            return None
