"""Contains the headers for the datafreame containing parsed employee data."""

from enum import StrEnum


class EmployeeDataHeaders(StrEnum):
    """Enum containing the headers for the datafreame containing parsed employee data."""

    SURNAME = "SURNAME"
    FIRST_NAME = "FIRST_NAME"
    BIRTH_NUM = "BIRTH_NUM"
    CONTRACT_START_DATE = "CONTRACT_START_DATE"
    CONTRACT_END_DATE = "CONTRACT_END_DATE"
    INSURANCE_CODE = "INSURANCE_CODE"
    DISABILITY_RECOGNISED_FROM = "DISABILITY_RECOGNISED_FROM"
    DISABILITY_RECOGNISED_TO = "DISABILITY_RECOGNISED_TO"
    DISABILITY_STATUS = "DISABILITY_STATUS"
    GROSS_PAY = "GROSS_PAY"
    PAY_FOR_ACTUAL_WORK = "PAY_FOR_ACTUAL_WORK"
    INSURANCE_PAYMENT = "INSURANCE_PAYMENT"
    EMPLOYEE_WORKED = "EMPLOYEE_WORKED"
