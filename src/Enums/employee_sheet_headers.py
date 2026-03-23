"""
This module defines an enum containing the column headers present in the employee sheet in the
template
"""
from enum import StrEnum


class EmployeeSheetHeaders(StrEnum):
    """
    This enum contains all the relevant column headers present in the employee sheet
    """
    SURNAME = "Příjmení"
    FIRST_NAME = "Jméno"
    BIRTH_NUM = "Rodné číslo"
    CONTRACT_START = "Datum vzniku  pracovního poměru7)"
    CONTRACT_END = "Datum skončení pracovního poměru7)"
    INSURANCE_COMPANY = "Kód zdravotní pojišťovny"
    DISABILITY_RECOGNITION_FROM = "Uznání invalidity/ ZZ  od"
    DISABILITY_RECOGNITION_TO = "Uznání invalidity/ ZZ  do"
    DISABILITY_STATUS = "Status TZP/ OZP 1.,2.st./ OZZ"
    GROSS_PAY = "Hrubá mzda / plat (v Kč)"
    INSURANCE_PAYMENT = "Odvod pojistného (v Kč)"
    EMPLOYEE_WORKED_THIS_MONTH = ("Informace o tom, zda osoba se zdravotním postižením alespoň po "
                                  "část měsíce pracovala")
