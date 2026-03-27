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
        self.template_manager: TemplateManager | None = None
        self.employee_data: dict[int, Employee] = {}
        self._data_months: dict[str, pd.DataFrame | None] | None = None
        self._year: int | None = None
        self._quarter: int | None = None

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
            ErrorHandler(error_code=ErrNoEnum.ERR_FAILED_TO_DOWNLOAD,
                         error_message=str(e))
            return False

        if not self.template_manager.download_template():
            raise ConnectionError("Nepodařilo se stáhnout Excel šablonu MPSV, zkontrolujte"
                                  "připojení k internetu a zkuste to prosím znovu.")

        if not self.template_manager.load_template_into_memory():
            ErrorHandler(error_code=ErrNoEnum.ERR_FAILED_TO_DOWNLOAD,
                         error_message="Nepodařilo se načíst šablonu, zkontrolujte, že je šablona "
                                       "v pořádku a zkuste to prosím znovu.")
        return True

    def load_data(self) -> bool:
        """
        Loads an Excel file into a pandas dataframe in the data attribute
        :return: bool indicating success or failure
        """
        try:
            self.data = pd.ExcelFile(path_or_buffer=self.file_path)

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
        if not self._set_year_and_quarter():
            print("fuck")

        self._process_employee_data()

        row: int = 12

        for employee in self.employee_data.values():
            self.template_manager.write_into_cell(sheet_name=TemplateSheetNames.EMPLOYEE_LIST.value,
                                                  col_header=(
                                                      "",
                                                      EmployeeSheetHeaders.FIRST_NAME.value
                                                  ),
                                                  row=row,
                                                  value=employee.get_first_name())
            self.template_manager.write_into_cell(sheet_name=TemplateSheetNames.EMPLOYEE_LIST.value,
                                                  col_header=(
                                                      "",
                                                      EmployeeSheetHeaders.SURNAME.value
                                                  ),
                                                  row=row,
                                                  value=employee.get_surname())
            self.template_manager.write_into_cell(sheet_name=TemplateSheetNames.EMPLOYEE_LIST.value,
                                                  col_header=(
                                                      "",
                                                      EmployeeSheetHeaders.BIRTH_NUM.value
                                                  ),
                                                  row=row,
                                                  value=employee.get_birth_num())
            self.template_manager.write_into_cell(sheet_name=TemplateSheetNames.EMPLOYEE_LIST.value,
                                                  col_header=(
                                                      "",
                                                      EmployeeSheetHeaders.CONTRACT_START.value
                                                  ),
                                                  row=row,
                                                  value=employee.get_contract_start_date())
            self.template_manager.write_into_cell(sheet_name=TemplateSheetNames.EMPLOYEE_LIST.value,
                                                  col_header=
                                                  (
                                                      "",
                                                      EmployeeSheetHeaders.CONTRACT_END.value
                                                  ),
                                                  row=row,
                                                  value=employee.get_contract_end_date())
            self.template_manager.write_into_cell(sheet_name=TemplateSheetNames.EMPLOYEE_LIST.value,
                                                  col_header=
                                                  (
                                                      "",
                                                      EmployeeSheetHeaders.INSURANCE_COMPANY.value
                                                  ),
                                                  row=row,
                                                  value=employee.get_insurance_code())
            self.template_manager.write_into_cell(sheet_name=TemplateSheetNames.EMPLOYEE_LIST.value,
                                                  col_header=
                                                  (
                                                      "",
                                                      EmployeeSheetHeaders.DISABILITY_RECOGNITION_FROM.value
                                                  ),
                                                  row=row,
                                                  value=employee.get_disability_recognised_from())
            self.template_manager.write_into_cell(sheet_name=TemplateSheetNames.EMPLOYEE_LIST.value,
                                                  col_header=
                                                  (
                                                      "Měsíc:",
                                                      EmployeeSheetHeaders.DISABILITY_RECOGNITION_TO.value
                                                  ),
                                                  row=row,
                                                  value=employee.get_disability_recognised_to())

            for month in self._data_months:

                self.template_manager.write_into_cell(sheet_name=TemplateSheetNames.EMPLOYEE_LIST.value,
                                                      col_header=
                                                      (
                                                          month,
                                                          EmployeeSheetHeaders.DISABILITY_STATUS.value
                                                      ),
                                                      row=row,
                                                      value=employee.get_disability_status())
                self.template_manager.write_into_cell(sheet_name=TemplateSheetNames.EMPLOYEE_LIST.value,
                                                      col_header=
                                                      (
                                                          month,
                                                          EmployeeSheetHeaders.GROSS_PAY.value
                                                      ),
                                                      row=row,
                                                      value=employee.get_gross_pay(month=MonthEnum(month)))
                self.template_manager.write_into_cell(sheet_name=TemplateSheetNames.EMPLOYEE_LIST.value,
                                                      col_header=
                                                      (
                                                          month,
                                                          EmployeeSheetHeaders.INSURANCE_PAYMENT.value
                                                      ),
                                                      row=row,
                                                      value=employee.get_insurance_payment(month=MonthEnum(month)))
                print(employee.get_surname())
                self.template_manager.write_into_cell(sheet_name=TemplateSheetNames.EMPLOYEE_LIST.value,
                                                      col_header=
                                                      (
                                                          month,
                                                          EmployeeSheetHeaders.EMPLOYEE_WORKED_THIS_MONTH.value
                                                      ),
                                                      row=row,
                                                      value=1 if employee.get_pay_for_actual_work
                                                                 (month=MonthEnum(month)) > 0
                                                      else 0)

            row += 1


        self._save_processed(f"{self._quarter}Q{self._year}seznam+zaměstnanců+OZP.xlsx")

        return True

    def _process_employee_data(self) -> bool:
        """
        Processes employee data in the input sheet and inputs them into the template
        :return: bool indicating success or failure
        """
        month_dataframes: list[pd.DataFrame] = [self.data.parse(self.data.sheet_names[0]),
                                                self.data.parse(self.data.sheet_names[1]),
                                                self.data.parse(self.data.sheet_names[2])]

        human_resources: pd.DataFrame = self.data.parse(self.data.sheet_names[3])

        for idx, key in enumerate(self._data_months):
            self._data_months[key] = month_dataframes[idx]

        for month_key, month_sheet in self._data_months.items():
            if month_sheet is None:
                continue

            month: MonthEnum = MonthEnum(month_key)

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

                    employee.set_birth_num(row[MonthHeaders.BIRTH_NUM.value])
                    employee.set_contract_start_date(row[MonthHeaders.CONTRACT_START.value])
                    employee.set_contract_end_date(row[MonthHeaders.CONTRACT_END.value])

                    employee.set_surname(hr_row[HumanResourcesHeaders.SURNAME.value])
                    employee.set_first_name(hr_row[HumanResourcesHeaders.FIRST_NAME])
                    employee.set_insurance_code(hr_row[HumanResourcesHeaders.INSURANCE_COMPANY])
                    employee.set_disability_status(DisabilityStatus(hr_row[HumanResourcesHeaders.DISABILITY_STATUS]))
                    employee.set_disability_recognised_from(hr_row[HumanResourcesHeaders.DISABILITY_START])

                else:
                    employee = self.employee_data[personal_num]

                employee.set_gross_pay(month,
                                       float(row[MonthHeaders.GROSS_PAY.value]))
                employee.set_insurance_payment(month,
                                               float(row[MonthHeaders.INSURANCE_PAYMENT.value]))
                employee.set_pay_for_actual_work(month,
                                                 float(row[MonthHeaders.PAY_FOR_ACTUAL_WORK.value]))

                self.employee_data[personal_num] = employee

        return True

    def _set_year_and_quarter(self) -> bool:
        """
        Sets which year and quarter the report is being generated for inside the template
        :return: bool indicating success or failure
        """
        months: tuple[int, ...] = tuple(int(m.split("_")[0]) for
                                        m in self.data.sheet_names if "_" in m)
        if months is None:
            ErrorHandler(error_code=ErrNoEnum.ERR_WORKING_WITH_EXCEL,
                         error_message="Chyba během zpracování vstupního souboru, prosím "
                                       "zkontrolujte formát Excelu na vstupu programu.")
            return False

        self._year = int(self.data.sheet_names[0].split("_")[1])

        match months:
            case Quarters.FIRST_QUARTER.value:
                self._quarter = 1
                self._data_months = {MonthEnum.JAN.value : None,
                                     MonthEnum.FEB.value : None,
                                     MonthEnum.MAR.value : None}
            case Quarters.SECOND_QUARTER.value:
                self._quarter = 2
                self._data_months = {MonthEnum.APR.value : None,
                                     MonthEnum.MAY.value : None,
                                     MonthEnum.JUN.value : None}
            case Quarters.THIRD_QUARTER.value:
                self._quarter = 3
                self._data_months = {MonthEnum.JUL.value : None,
                                     MonthEnum.AUG.value : None,
                                     MonthEnum.SEP.value : None}
            case Quarters.FOURTH_QUARTER.value:
                self._quarter = 4
                self._data_months = {MonthEnum.OCT.value : None,
                                     MonthEnum.NOV.value : None,
                                     MonthEnum.DEC.value : None}
            case _:
                return False

        self.template_manager.write_into_cell(sheet_name=TemplateSheetNames.INTRO_SHEET,
                                              value=self._quarter,
                                              row=5,
                                              col=3)

        self.template_manager.write_into_cell(sheet_name=TemplateSheetNames.INTRO_SHEET,
                                              value=self._year,
                                              row=5,
                                              col=8)

        return True

    def _save_processed(self, filename: str) -> bool:
        """
        Saves the processed data into an Excel file with a specified filename
        :param filename: desired name of the output file
        :return: bool indicating success or failure
        """
        if not self.output_directory:
            ErrorHandler(error_code=ErrNoEnum.ERR_FAILED_TO_SAVE,
                         error_message="Složka pro výstup nebyla nastavena, zkuste to "
                                       "prosím znovu.")
            return False

        final_path: Path = self.output_directory / filename

        if final_path.suffix != ".xlsx":
            final_path = final_path.with_suffix(".xlsx")

        return self.template_manager.write_file(final_path)
