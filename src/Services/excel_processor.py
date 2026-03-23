"""
This module contains the ExcelProcessor class used for processing the provided input Excel file
"""
from pathlib import Path

import pandas as pd

from src.Enums import MonthEnum
from src.Enums.disability_status_enum import DisabilityStatus
from src.Enums.employee_sheet_headers import EmployeeSheetHeaders
from src.Enums.err_no_enum import ErrNoEnum
from src.Enums.human_resources_headers_enum import HumanResourcesHeaders
from src.Enums.month_headers_enum import MonthHeaders
from src.Enums.quarter_enum import Quarters
from src.Enums.template_sheet_names_enum import TemplateSheetNames
from src.Mappers.int_month_mapper import IntMonthMapper
from src.Services.template_manager import TemplateManager
from src.Utils.employee import Employee
from src.Utils.error_handler import ErrorHandler


class ExcelProcessor:
    """
    Class made for handling loading and processing the Excel files
    """
    def __init__(self) -> None:
        self.file_path = None
        self.output_directory = None
        self.data: pd.ExcelFile | None = None
        self.template: pd.ExcelFile | None = None
        self.template_employee_sheet: pd.DataFrame | None = None
        self.template_intro_sheet: pd.DataFrame | None = None
        self.template_manager: TemplateManager | None = None
        self.employee_data: dict[int, Employee] = {}
        self._data_months: dict[str, pd.DataFrame | None] | None = None

    def set_input(self, file_path: Path) -> None:
        """
        This method sets the filepath to the input Excel file.
        :return: True if successful, False otherwise
        """
        self.file_path = file_path

    def set_output_directory(self, output_directory: Path) -> None:
        """
        This method attempts to set the output directory for the modified Excel file
        :param output_directory: string indicating the filepath to the output directory
        :return: True if successful, False otherwise
        """
        self.output_directory = output_directory

    def load_template(self) -> bool:
        """
        This method loads the template Excel file into a pandas dataframe in order to be edited,
        loads sheets that will be explicitly required into separate attributes
        :return: bool indicating if the template was successfully loaded
        """
        try:
            self.template_manager = TemplateManager(r"https://mpsv.gov.cz/cms/documents/57e12a5e-05b3-6511-0b8a-25dab64d5396/seznam%20zam%C4%9Bstnanc%C5%AF%20OZP_verze%2023_9_2025.xlsx")
        except PermissionError as e:
            ErrorHandler(error_code=ErrNoEnum.ERR_FAILED_TO_DOWNLOAD, error_message=str(e))
            return False

        if not self.template_manager.download_template():
            raise ConnectionError("Nepodařilo se stáhnout Excel šablonu MPSV, zkontrolujte"
                                  "připojení k internetu a zkuste to prosím znovu.")
        return True

    def load_data(self) -> bool:
        """
        Loads an Excel file into a pandas dataframe in the data attribute
        :return: bool indicating success or failure
        """
        try:
            self.data = pd.ExcelFile(io=self.file_path)

        except OSError:
            ErrorHandler(error_code=ErrNoEnum.ERR_OPENING_EXCEL,
                         error_message="Nepodařilo se otevřít Excel soubor, prosím ujistěte se, že"
                                       "jej nemáte nikde otevřený a zkuste to znovu.")
            return False
        return True

    def process_input_data(self) -> bool:
        """
        Processes the input Excel file and populates the template with data extracted from it
        :return: bool indicating success or failure
        """
        self._process_employee_data()

        row: int = 12

        for _, employee in self.employee_data:
            self.template_manager.write_into_cell(sheet_name=TemplateSheetNames.EMPLOYEE_LIST,
                                                  col_header=(
                                                      "",
                                                      EmployeeSheetHeaders.FIRST_NAME
                                                  ),
                                                  row=row,
                                                  value=employee.get_first_name())
            self.template_manager.write_into_cell(sheet_name=TemplateSheetNames.EMPLOYEE_LIST,
                                                  col_header=(
                                                      "",
                                                      EmployeeSheetHeaders.SURNAME
                                                  ),
                                                  row=row,
                                                  value=employee.get_surname())
            self.template_manager.write_into_cell(sheet_name=TemplateSheetNames.EMPLOYEE_LIST,
                                                  col_header=(
                                                      "",
                                                      EmployeeSheetHeaders.BIRTH_NUM
                                                  ),
                                                  row=row,
                                                  value=employee.get_birth_num())
            self.template_manager.write_into_cell(sheet_name=TemplateSheetNames.EMPLOYEE_LIST,
                                                  col_header=(
                                                      "",
                                                      EmployeeSheetHeaders.CONTRACT_START
                                                  ),
                                                  value=employee.get_contract_start())
            self.template_manager.write_into_cell(sheet_name=TemplateSheetNames.EMPLOYEE_LIST,
                                                  col_header=
                                                  (
                                                      "",
                                                      EmployeeSheetHeaders.CONTRACT_END
                                                  ),
                                                  value=employee.get_contract_end())
            self.template_manager.write_into_cell(sheet_name=TemplateSheetNames.EMPLOYEE_LIST,
                                                  col_header=
                                                  (
                                                      "",
                                                      EmployeeSheetHeaders.INSURANCE_COMPANY
                                                  ),
                                                  value=employee.get_insurance_company())
            self.template_manager.write_into_cell(sheet_name=TemplateSheetNames.EMPLOYEE_LIST,
                                                  col_header=
                                                  (
                                                      "",
                                                      EmployeeSheetHeaders.DISABILITY_RECOGNITION_FROM
                                                  ),
                                                  value=employee.get_disability_recognition_from())
            self.template_manager.write_into_cell(sheet_name=TemplateSheetNames.EMPLOYEE_LIST,
                                                  col_header=
                                                  (
                                                      "Měsíc:",
                                                      EmployeeSheetHeaders.DISABILITY_RECOGNITION_TO
                                                  ),
                                                  value=employee.get_disability_recognition_to())
            self.template_manager.write_into_cell(sheet_name=TemplateSheetNames.EMPLOYEE_LIST,
                                                  col_header=
                                                  (
                                                      next(iter(self._data_months)),
                                                      EmployeeSheetHeaders.DISABILITY_STATUS
                                                  ),
                                                  value=employee.get_disability_status())

        return True

    def _clean_indexing(self):
        self.template_employee_sheet.columns = pd.MultiIndex.from_tuples(
            [("" if "Unnamed" in a else a, b) for a, b in self.template_employee_sheet.columns]
        )

    def _process_employee_data(self) -> bool:
        """
        Processes employee data in the input sheet and inputs them into the template
        :return: bool indicating success or failure
        """
        month_dataframes: list[pd.DataFrame] = [self.data.parse(self.data.sheet_names[0]),
                                                self.data.parse(self.data.sheet_names[1]),
                                                self.data.parse(self.data.sheet_names[2])]

        human_resources: pd.DataFrame = self.data.parse(io=self.data.sheet_names[3],
                                                        parse_dates=[HumanResourcesHeaders.DISABILITY_START])

        for idx, key in enumerate(self._data_months):
            self._data_months[key] = month_dataframes[idx]

        for month_sheet in self._data_months:
            month = IntMonthMapper.from_int(int(month_sheet.attrs["sheet_name"].split("_")[0]))
            for _, row in month_sheet.iterrows():
                personal_num: int = int(row[MonthHeaders.PERSONAL_NUM])

                if personal_num not in self.employee_data:
                    hr_matches: pd.DataFrame = human_resources.loc[
                        human_resources[HumanResourcesHeaders.PERSONAL_NUM] == personal_num
                    ]
                    if hr_matches.empty:
                        ErrorHandler(
                            error_code=ErrNoEnum.ERR_WORKING_WITH_EXCEL,
                            error_message="Něco se nepodařilo, zkontrolujte prosím, že každý "
                            "zaměstnanec je zaveden v tabulce personalistika",
                        )
                        return False

                    hr_row: pd.DataFrame = hr_matches.iloc[0]

                    employee: Employee = Employee()

                    employee.set_birth_num(row[MonthHeaders.BIRTH_NUM])
                    employee.set_contract_start_date(row[MonthHeaders.CONTRACT_START])
                    employee.set_contract_end_date(row[MonthHeaders.CONTRACT_END])

                    employee.set_surname(hr_row[HumanResourcesHeaders.SURNAME])
                    employee.set_first_name(hr_row[HumanResourcesHeaders.FIRST_NAME])
                    employee.set_insurance_code(hr_row[HumanResourcesHeaders.INSURANCE_COMPANY])
                    employee.set_disability_status(DisabilityStatus(hr_row[HumanResourcesHeaders.DISABILITY_STATUS]))
                    employee.set_disability_recognised_from(hr_row[HumanResourcesHeaders.DISABILITY_START])

                else:
                    employee = self.employee_data[personal_num]

                employee.set_gross_pay(month,
                                       float(row[MonthHeaders.GROSS_PAY]))
                employee.set_insurance_payment(month,
                                               float(row[MonthHeaders.INSURANCE_PAYMENT]))
                employee.set_pay_for_actual_work(month,
                                                 float(row[MonthHeaders.PAY_FOR_ACTUAL_WORK]))

                self.employee_data[personal_num] = employee

        return True

    def _set_year_and_quarter(self) -> bool:
        """
        Sets which year and quarter the report is being generated for inside the template
        :return: bool indicating success or failure
        """
        months: set[int] = {int(m.split("_")[0]) for m in self.data.sheet_names if "_" in m}
        if months is None:
            ErrorHandler(error_code=ErrNoEnum.ERR_WORKING_WITH_EXCEL,
                         error_message="Chyba během zpracování vstupního souboru, prosím "
                                       "zkontrolujte formát Excelu na vstupu programu.")
            return False

        year: int = int(self.data.sheet_names[0].split("_")[1])

        match months:
            case Quarters.FIRST_QUARTER:
                quarter: int = 1
                self._data_months = {MonthEnum.JAN : None,
                                     MonthEnum.FEB : None,
                                     MonthEnum.MAR : None}
            case Quarters.SECOND_QUARTER:
                quarter: int = 2
                self._data_months = {MonthEnum.APR : None,
                                     MonthEnum.MAY : None,
                                     MonthEnum.JUN : None}
            case Quarters.THIRD_QUARTER:
                quarter: int = 3
                self._data_months = {MonthEnum.JUL : None,
                                     MonthEnum.AUG : None,
                                     MonthEnum.SEP : None}
            case Quarters.FOURTH_QUARTER:
                quarter: int = 4
                self._data_months = {MonthEnum.OCT : None,
                                     MonthEnum.NOV : None,
                                     MonthEnum.DEC : None}
            case _:
                return False

        self.template_manager.write_into_cell(sheet_name=TemplateSheetNames.INTRO_SHEET,
                                              value=quarter,
                                              row=5,
                                              col=3)

        self.template_manager.write_into_cell(sheet_name=TemplateSheetNames.INTRO_SHEET,
                                              value=year,
                                              row=5,
                                              col=8)

        return True
