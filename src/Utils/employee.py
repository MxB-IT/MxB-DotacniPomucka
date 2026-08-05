"""Defines a container for employee data extracted from the input sheet."""
from datetime import datetime

import pandas as pd

from Enums import ErrNoEnum, MonthEnum
from Enums.disability_status_enum import DisabilityStatus
from Utils.app_error import AppError


class Employee:
    """Data structure used to hold employee data extracted from the input sheet."""

    def __init__(self) -> None:
        """Initialise the Employee object.

        Initialises the Employee object, setting all internal attributes to None or blanks.
        :return: None.
        """
        self.__surname: str | None = None
        self.__first_name: str | None = None
        self.__birth_num: str | None = None
        self.__contract_start_date: datetime | None = None
        self.__contract_end_date: datetime | None = None
        self.__insurance_code: int | None = None
        self.__disability_recognised_from: datetime | None = None
        self.__disability_recognised_to: datetime | None = None
        self.__disability_status: DisabilityStatus | None = None
        self.__gross_pay: dict[MonthEnum, float] = {}
        self.__pay_for_actual_work: dict[MonthEnum, float] = {}
        self.__insurance_payment: dict[MonthEnum, float] = {}

    def set_surname(self, surname: str) -> None:
        """Set the surname to the passed str value.

        Setter for the surname private attribute.
        :param surname: surname of the employee to save in the Employee instance
        :return: None
        """
        self.__surname = surname

    def get_surname(self) -> str:
        """Get the surname held by the Employee instance.

        Getter for the surname private attribute, checks whether surname is blank and shows an
        error to the user if it is, to ensure the user knows why the writing failed.
        :return: Surname of the employee if it exists, None otherwise.
        :raises AppError: If surname is not set.
        """
        if self.__surname is None:
            raise AppError(error_code=ErrNoEnum.ERR_EMPLOYEE_MANDATORY_ATTR_NOT_SET,
                           error_message="Chyba během zpracování Excelu, zkontrolujte, že každý "
                                "zaměstnanec má na vstupu zadané příjmení a zkuste to prosím "
                                "znovu.")

        return self.__surname

    def get_first_name(self) -> str:
        """Get the first name held by the Employee instance.

        Getter for the first name private attribute, checks whether first name is blank and shows
        an error to the user if it is, to ensure the user knows why the writing failed.
        :return: First name of the employee if it exists, None otherwise
        :raises AppError: If first name is not set.
        """
        if self.__first_name is None:
            raise AppError(error_code=ErrNoEnum.ERR_EMPLOYEE_MANDATORY_ATTR_NOT_SET,
                           error_message="Chyba během zpracování Excelu, zkontrolujte, že každý "
                                "zaměstnanec má na vstupu zadané křestní jméno a zkuste to "
                                "prosím znovu.")

        return self.__first_name

    def set_first_name(self, first_name: str) -> None:
        """Set the Employee instance's first name attribute to the passed str value.

        Setter for the first_name private attribute
        :param first_name: first_name to assign to the employee instance
        :return: None
        """
        self.__first_name = first_name

    def set_birth_num(self, birth_num: str) -> None:
        """Set the Employee instance's birth number to the passed str value.

        Setter for the birth_num private attribute.
        :param birth_num: birth_num to assign to the employee instance
        :return: None
        """
        self.__birth_num = birth_num

    def get_birth_num(self) -> str:
        """Get the birth number held by the Employee instance.

        Getter for the birth number private attribute, since birth num can be blank (with
        foreigners for example), it is not checked for blankness.
        :return: birth number of the employee if it exists, None otherwise.
        """
        if self.__birth_num is None:
            return "NEZNÁMÉ!"
        return self.__birth_num

    def set_contract_start_date(self, contract_start_date: datetime) -> None:
        """Set the contract start date attribute of the employee instance.

        Setter for the date_of_contract_start private attribute
        :param contract_start_date: date of contrast start to assign to the employee instance
        :return: None
        """
        self.__contract_start_date = contract_start_date

    def get_contract_start_date(self) -> datetime:
        """Get the contract start date attribute of the employee instance.

        Getter for the contract start date private attribute, checks whether contract start date
        is blank and shows an error to the user if it is, to ensure the user knows why the writing
        failed
        :return: contract start date for the employee if it exists, None otherwise
        :raises AppError: if contract start date is not set
        """
        if self.__contract_start_date is None:
            raise AppError(error_code=ErrNoEnum.ERR_EMPLOYEE_MANDATORY_ATTR_NOT_SET,
                           error_message="Chyba během zpracování Excelu, zkontrolujte, že každý "
                                "zaměstnanec má na vstupu zadané datum vzniku pracovního poměru a "
                                "zkuste to prosím znovu.")
        return self.__contract_start_date

    def set_contract_end_date(self, contract_end_date: datetime) -> None:
        """Set the contract end date attribute of the Employee instance.

        Setter for the contract end date private attribute.
        :param contract_end_date: Contract end date to assign to the employee instance.
        :return: None.
        """
        self.__contract_end_date = contract_end_date

    def get_contract_end_date(self) -> datetime | None:
        """Get the contract end date attribute of the Employee instance.

        Getter for the contract end date private attribute, since this information is not mandatory
        to fill in, this getter does not error when the attribute is None.
        :return: Contract end date for the employee if it exists, None otherwise
        :raises AppError: If contract end date is not set.
        """
        return self.__contract_end_date

    def set_insurance_code(self, insurance_code: int) -> None:
        """Set the insurance code attribute of the Employee instance.

        Setter for the insurance code private attribute.
        :param insurance_code: Insurance code to assign to the employee instance.
        :return: None.
        """
        self.__insurance_code = insurance_code

    def get_insurance_code(self) -> int | None:
        """Get the insurance code attribute of the Employee instance.

        Getter for the insurance code private attribute, checks whether insurance code is blank and
        shows an error to the user if it is, to ensure the user knows why the writing failed
        :return: insurance code for the employee if it exists, None otherwise
        """
        if self.__insurance_code is None:
            raise AppError(error_code=ErrNoEnum.ERR_EMPLOYEE_MANDATORY_ATTR_NOT_SET,
                           error_message="Chyba během zpracování Excelu, zkontrolujte, že každý "
                                "zaměstnanec má na vstupu zadané číslo pojišťovny a zkuste to "
                                "prosím znovu.")
        return self.__insurance_code

    def set_disability_recognised_from(self, disability_recognised_from: datetime) -> None:
        """Set the disability recognised from attribute of the Employee instance.

        Setter for the private attribute signifying from when the employees disability is
        officially recognised
        :param disability_recognised_from: DateTime representation of from what date the employees
        disability is officially recognised from
        :return: None
        """
        self.__disability_recognised_from = disability_recognised_from

    def get_disability_recognised_from(self) -> datetime | None:
        """Get the disability recognised from attribute held by the Employee instance.

        Getter for the disability recognised from private attribute, checks whether disability
        recognised from is blank and shows an error to the user if it is, to ensure the user knows
        why the program failed.
        :return: Disability recognised from for the employee if it exists, None otherwise.
        :raises AppError: If disability recognised from is not set.
        """
        if self.__disability_recognised_from is None:
            raise AppError(error_code=ErrNoEnum.ERR_EMPLOYEE_MANDATORY_ATTR_NOT_SET,
                           error_message="Chyba během zpracování Excelu, zkontrolujte, že každý "
                                "zaměstnanec má na vstupu zadané odkdy je mu uznávána invalidita "
                                "a zkuste to prosím znovu.")
        return self.__disability_recognised_from

    def set_disability_recognised_to(self, disability_recognised_to: datetime) -> None:
        """Set the disability recognised to attribute of the Employee instance.

        Setter for the private attribute signifying until which date the employees disability is
        officially recognised
        :param disability_recognised_to: DateTime representation of until which date the employees
        disability is officially recognised from
        :return: None
        """
        self.__disability_recognised_to = disability_recognised_to

    def get_disability_recognised_to(self) -> datetime | None:
        """Get the disability recognised to attribute held by the Employee instance.

        Getter for the disability recognised to private attribute, since this information is not
        mandatory to fill in, this getter does not error when the attribute is None
        :return: disability recognised to for the employee if it exists, None otherwise
        """
        return self.__disability_recognised_to

    def set_disability_status(self, disability_status: DisabilityStatus) -> None:
        """Set the disability status attribute of the Employee instance.

        Setter for the disability status private attribute.
        :param disability_status: Disability status to assign to the employee instance.
        :return: None.
        """
        self.__disability_status = disability_status

    def get_disability_status(self) -> DisabilityStatus:
        """Get the disability status attribute of the Employee instance.

        Getter for the disability status private attribute, checks whether disability status is
        blank and shows an error to the user if it is, to ensure the user knows why the writing
        failed.
        :return: Disability status for the employee if it exists, None otherwise.
        :raises AppError: If disability status is not set.
        """
        if self.__disability_status is None:
            raise AppError(error_code=ErrNoEnum.ERR_EMPLOYEE_MANDATORY_ATTR_NOT_SET,
                           error_message="Chyba během zpracování Excelu, zkontrolujte, že každý "
                                "zaměstnanec má na vstupu zadaný status invalidity a zkuste to "
                                "prosím znovu.")

        return self.__disability_status

    def set_gross_pay(self, month: MonthEnum, pay: float) -> None:
        """Set the gross pay for a given month of the Employee instance.

        Setter for the gross_pay private attribute, sets pay for the chosen month.
        :param month: Month for which the salary is relevant.
        :param pay: The employee's salary before tax.
        :return: None.
        """
        self.__gross_pay[month] = pay

    def get_gross_pay(self, month: MonthEnum) -> float:
        """Get the gross pay for a given month held by the Employee instance.

        Getter for the gross_pay for a given month private attribute, checks whether pay for the
        month is blank and shows an error to the user if it is, to ensure the user knows why the
        writing failed.
        :param month: Month from which to get the employee's gross pay.
        :return: Gross pay for a given month for the employee if it exists, None otherwise.
        """
        try:
            return self.__gross_pay[month]
        except KeyError:
            return 0

    def set_pay_for_actual_work(self, month: MonthEnum, pay: float) -> None:
        """Set the pay for actual work for a given month of the Employee instance.

        Setter for the pay_for_actual_month private attribute, sets pay for the chosen month.
        :param month: Month for which to set the pay_for_actual_work.
        :param pay: How much the employee was paid for actual work.
        :return: None.
        """
        if pay:
            self.__pay_for_actual_work[month] = pay
        else:
            self.__pay_for_actual_work[month] = 0

    def get_pay_for_actual_work(self, month: MonthEnum) -> float:
        """Get the pay for actual work for a given month held by the Employee instance.

        Getter for the pay_for_actual_work attribute, checks whether pay for_actual_work is blank
        and since this attribute is mandatory (the government Excel template requires it), errors
        out, displaying an error to the user if it isn't set
        :param month: month for which to get the pay_for_actual_work
        :return: pay for a given month for the employee if it exists, None otherwise
        """
        try:
            return self.__pay_for_actual_work[month]
        except KeyError:
            return 0

    def set_insurance_payment(self, month: MonthEnum, insurance_payment: float) -> None:
        """Set the insurance payment attribute for a given month of the Employee instance.

        Setter for the insurance payment private attribute, sets insurance payment for the chosen
        month
        :param month: month for which to set the amount of insurance payment provided by the
        employer
        :param insurance_payment: amount of money paid
        :return: None
        """
        self.__insurance_payment[month] = insurance_payment

    def get_insurance_payment(self, month: MonthEnum) -> float:
        """Get the insurance payment for a given month held by the Employee instance.

        Getter for the insurance payment for a given month private attribute, checks whether
        insurance payment for the month is blank and shows an error to the user if it is, to ensure
        the user knows why the writing failed
        :param month: month from which to get the amount of insurance payment provided by the
        employer
        :return: insurance payment for a given month provided bny the employer if it exists, None
        otherwise
        """
        try:
            return self.__insurance_payment[month]
        except KeyError:
            return 0

    def was_active_in_quarter(self, months: dict[str, pd.DataFrame | None]) -> bool:
        """Check whether the employee worked in the considered quarter.

        Checks whether the employee was active in the quarter
        :param months: months to check for activity
        :return: boolean indicating whether the employee was active in the quarter
        """
        return any(
            self.get_pay_for_actual_work(MonthEnum(m)) > 0 or
            self.get_gross_pay(MonthEnum(m)) > 0 for m in months
        )
