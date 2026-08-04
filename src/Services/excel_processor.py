"""Contains the ExcelProcessor class used for processing the provided input Excel file."""
import time
from pathlib import Path
from typing import cast

import pandas as pd

from src.Enums import MonthEnum
from src.Enums.employee_sheet_headers import EmployeeSheetHeaders
from src.Enums.err_no_enum import ErrNoEnum
from src.Enums.human_resources_headers_enum import HumanResourcesHeaders
from src.Enums.month_headers_enum import MonthHeaders
from src.Enums.quarter_enum import Quarters
from src.Enums.template_sheet_names_enum import TemplateSheetNames
from src.Mappers.disability_type_mapper import DisabilityTypeMapper
from src.Mappers.insurance_company_mapper import InsuranceCompanyMapper
from src.Services.template_manager import TemplateManager
from src.Utils.app_error import AppError
from src.Utils.employee import Employee
from src.Utils.error_handler import ErrorHandler


class ExcelProcessor:
    """Class made for handling loading and processing the Excel files."""

    def __init__(self) -> None:
        """Initialise the ExcelProcessor.

        Initialises the ExcelProcessor, initialising all internal variables as blanks
        """
        self.file_path: Path | None = None
        self.output_directory: Path | None = None
        self.data: pd.ExcelFile | None = None
        self.template: pd.ExcelFile | None = None
        self.template_manager: TemplateManager | None = None
        self.employee_data: dict[int, Employee] = {}
        self.data_months: dict[str, pd.DataFrame | None] = {}
        self.__year: int | None = None
        self.__quarter: int | None = None

    def set_input(self, file_path: Path) -> None:
        """Set filepath to the input Excel file.

        This method sets the filepath to the input Excel file.
        :return: True if successful, False otherwise
        """
        self.file_path = file_path

    def set_output_directory(self, output_directory: Path) -> None:
        """Set output directory to work with.

        This method attempts to set the output directory for the modified Excel file
        :param output_directory: string indicating the filepath to the output directory
        :return: True if successful, False otherwise
        """
        self.output_directory = output_directory

    def load_template(self) -> None:
        """Load template Excel file via openpyxl.

        This method loads the template Excel file into a pandas dataframe in order to be edited,
        loads sheets that will be explicitly required into separate attributes
        :return: None, raises an error if failed
        """
        try:
            self.template_manager = TemplateManager(r"https://mpsv.gov.cz/cms/documents/57e12a5e-05b3-6511-0b8a-25dab64d5396/seznam%20zam%C4%9Bstnanc%C5%AF%20OZP_verze%2023_9_2025.xlsx")
        except PermissionError as e:
            raise AppError(error_code=ErrNoEnum.ERR_FAILED_TO_DOWNLOAD,
                           error_message="Chyba při stahování souboru, program nemá"
                                         " dostatečná práva.") from e

        if not self.template_manager.download_template():
            raise AppError(error_code=ErrNoEnum.ERR_FAILED_TO_DOWNLOAD,
                           error_message="Nepodařilo se stáhnout Excel šablonu MPSV, zkontrolujte"
                                         "připojení k internetu a zkuste to prosím znovu.")

        if not self.template_manager.load_template_into_memory():
            raise AppError(error_code=ErrNoEnum.ERR_FAILED_TO_DOWNLOAD,
                           error_message="Nepodařilo se načíst šablonu, zkontrolujte, že je"
                                         " šablona v pořádku a zkuste to prosím znovu.")

    def load_data(self) -> None:
        """Load Excel file containing the data to process.

        Loads an Excel file into a pandas dataframe in the data attribute
        :return: None, raises an error if failed
        """
        try:
            self.data = pd.ExcelFile(path_or_buffer=self.file_path)

        except OSError as e:
            raise AppError(error_code=ErrNoEnum.ERR_OPENING_EXCEL,
                           error_message="Nepodařilo se otevřít Excel soubor, prosím ujistěte se, "
                                         "že jej nemáte nikde otevřený a zkuste to znovu.") from e

    def process_input_data(self) -> bool:
        """Process the input file.

        Processes the input Excel file and populates the template with data extracted from it
        :return: bool indicating success or failure
        """
        self.__set_year_and_quarter()

        if self.template_manager is None:
            raise AppError(error_code=ErrNoEnum.INTERNAL_ERROR,
                           error_message="Interní chyba programu, zkuste to prosím znovu")

        if not self.template_manager.reload_template():
            raise AppError(error_code=ErrNoEnum.INTERNAL_ERROR,
                           error_message="Chyba během znovunačítání Excelu")

        if self.data_months == {}:
            return False

        headers: tuple[tuple[str, ...], ...] = self.__construct_headers()

        self.template_manager.build_col_map(TemplateSheetNames.EMPLOYEE_LIST.value,
                                            headers)

        self.__process_employee_data()

        row: int = 13

        for employee in self.employee_data.values():

            if not employee.was_active_in_quarter(months=self.data_months):
                continue

            time.sleep(0.001)

            for month in self.data_months:

                self.template_manager.write_into_cell(sheet_name=TemplateSheetNames.EMPLOYEE_LIST.value,
                                                      col_header=
                                                      (
                                                          month,
                                                          EmployeeSheetHeaders.DISABILITY_STATUS.value,
                                                      ),
                                                      row=row,
                                                      value=employee.get_disability_status())
                self.template_manager.write_into_cell(sheet_name=TemplateSheetNames.EMPLOYEE_LIST.value,
                                                      col_header=
                                                      (
                                                          month,
                                                          EmployeeSheetHeaders.GROSS_PAY.value,
                                                      ),
                                                      row=row,
                                                      value=employee.get_gross_pay(month=MonthEnum(month)))
                self.template_manager.write_into_cell(sheet_name=TemplateSheetNames.EMPLOYEE_LIST.value,
                                                      col_header=
                                                      (
                                                          month,
                                                          EmployeeSheetHeaders.INSURANCE_PAYMENT.value,
                                                      ),
                                                      row=row,
                                                      value=employee.get_insurance_payment(month=MonthEnum(month)))
                self.template_manager.write_into_cell(sheet_name=TemplateSheetNames.EMPLOYEE_LIST.value,
                                                      col_header=
                                                      (
                                                          month,
                                                          EmployeeSheetHeaders.EMPLOYEE_WORKED_THIS_MONTH.value,
                                                      ),
                                                      row=row,
                                                      value=1 if employee.get_pay_for_actual_work
                                                                 (month=MonthEnum(month)) > 0
                                                      else 0)

            self.template_manager.write_into_cell(sheet_name=TemplateSheetNames.EMPLOYEE_LIST.value,
                                                  col_header=(
                                                      EmployeeSheetHeaders.BLANK.value,
                                                      EmployeeSheetHeaders.FIRST_NAME.value,
                                                  ),
                                                  row=row,
                                                  value=employee.get_first_name())
            self.template_manager.write_into_cell(sheet_name=TemplateSheetNames.EMPLOYEE_LIST.value,
                                                  col_header=(
                                                      EmployeeSheetHeaders.BLANK.value,
                                                      EmployeeSheetHeaders.SURNAME.value,
                                                  ),
                                                  row=row,
                                                  value=employee.get_surname())
            self.template_manager.write_into_cell(sheet_name=TemplateSheetNames.EMPLOYEE_LIST.value,
                                                  col_header=(
                                                      EmployeeSheetHeaders.BLANK.value,
                                                      EmployeeSheetHeaders.BIRTH_NUM.value,
                                                  ),
                                                  row=row,
                                                  value=employee.get_birth_num())
            self.template_manager.write_into_cell(sheet_name=TemplateSheetNames.EMPLOYEE_LIST.value,
                                                  col_header=(
                                                      EmployeeSheetHeaders.BLANK.value,
                                                      EmployeeSheetHeaders.CONTRACT_START.value,
                                                  ),
                                                  row=row,
                                                  value=employee.get_contract_start_date())
            self.template_manager.write_into_cell(sheet_name=TemplateSheetNames.EMPLOYEE_LIST.value,
                                                  col_header=
                                                  (
                                                      EmployeeSheetHeaders.BLANK.value,
                                                      EmployeeSheetHeaders.CONTRACT_END.value,
                                                  ),
                                                  row=row,
                                                  value=employee.get_contract_end_date())
            self.template_manager.write_into_cell(sheet_name=TemplateSheetNames.EMPLOYEE_LIST.value,
                                                  col_header=
                                                  (
                                                      EmployeeSheetHeaders.BLANK.value,
                                                      EmployeeSheetHeaders.INSURANCE_COMPANY.value,
                                                  ),
                                                  row=row,
                                                  value=employee.get_insurance_code())
            self.template_manager.write_into_cell(sheet_name=TemplateSheetNames.EMPLOYEE_LIST.value,
                                                  col_header=
                                                  (
                                                      EmployeeSheetHeaders.BLANK.value,
                                                      EmployeeSheetHeaders.DISABILITY_RECOGNITION_FROM.value,
                                                  ),
                                                  row=row,
                                                  value=employee.get_disability_recognised_from())
            self.template_manager.write_into_cell(sheet_name=TemplateSheetNames.EMPLOYEE_LIST.value,
                                                  col_header=
                                                  (
                                                      "Měsíc:",
                                                      EmployeeSheetHeaders.DISABILITY_RECOGNITION_TO.value,
                                                  ),
                                                  row=row,
                                                  value=employee.get_disability_recognised_to())

            row += 1


        self.__save_processed(f"{self.__quarter}Q{self.__year}seznam+zaměstnanců+OZP.xlsx")

        return True

    def __process_employee_data(self) -> bool:
        """Process employee data and create Employee objects representing them.

        Processes employee data in the input sheet and inputs them into the template.
        :return: bool indicating success or failure.
        """
        if self.data is None:
            raise AppError(error_code=ErrNoEnum.INTERNAL_ERROR,
                           error_message="Interní chyba programu")

        month_dataframes: list[pd.DataFrame] = [
            cast("pd.DataFrame", self.data.parse(self.data.sheet_names[0])),
            cast("pd.DataFrame", self.data.parse(self.data.sheet_names[1])),
            cast("pd.DataFrame", self.data.parse(self.data.sheet_names[2])),
        ]

        human_resources: pd.DataFrame = cast(
            "pd.DataFrame",
            self.data.parse(self.data.sheet_names[3]),
        )

        for idx, key in enumerate(self.data_months):
            self.data_months[key] = month_dataframes[idx]

        for month_key, month_sheet in self.data_months.items():
            if month_sheet is None:
                continue

            month: MonthEnum = MonthEnum(month_key)

            records = month_sheet.to_dict("records")

            for row in records:
                personal_num: int = int(row[MonthHeaders.PERSONAL_NUM])

                if personal_num not in self.employee_data:
                    hr_matches: pd.DataFrame = human_resources.loc[
                        human_resources[HumanResourcesHeaders.PERSONAL_NUM] == personal_num
                    ]
                    if hr_matches.empty:
                        raise AppError(
                            error_code=ErrNoEnum.ERR_EMPLOYEE_MISSING,
                            error_message="Něco se nepodařilo, zkontrolujte prosím, že každý zaměstnanec je zaveden v "
                            "tabulce personalistika, případně že máte správnou tabulku personalistika.",
                        )

                    hr_row: pd.DataFrame = hr_matches.iloc[0]

                    employee: Employee = Employee()

                    employee.set_birth_num(row[MonthHeaders.BIRTH_NUM.value])
                    employee.set_contract_start_date(row[MonthHeaders.CONTRACT_START.value])

                    employee.set_surname(hr_row[HumanResourcesHeaders.SURNAME.value])
                    employee.set_first_name(hr_row[HumanResourcesHeaders.FIRST_NAME])
                    employee.set_insurance_code(InsuranceCompanyMapper
                                                .from_str(hr_row[HumanResourcesHeaders.INSURANCE_COMPANY]))
                    employee.set_disability_status(DisabilityTypeMapper
                                                   .from_int(int(hr_row[HumanResourcesHeaders.DISABILITY_STATUS])))
                    employee.set_disability_recognised_from(hr_row[HumanResourcesHeaders.DISABILITY_START])
                    try:
                        employee.get_disability_recognised_from()
                        employee.get_disability_status()
                    except AppError:
                        continue

                else:
                    employee = self.employee_data[personal_num]

                if employee.get_contract_end_date() is None and not pd.isna(row[MonthHeaders.CONTRACT_END.value]):
                    employee.set_contract_end_date(row[MonthHeaders.CONTRACT_END.value])

                employee.set_gross_pay(month,
                                       float(row[MonthHeaders.GROSS_PAY.value]))

                insurance_payment: float = (float(row[MonthHeaders.COMPANY_INSURANCE.value]) +
                                            float(row[MonthHeaders.COMPANY_SOCIAL_SEC.value]))

                employee.set_insurance_payment(month,
                                               insurance_payment)
                employee.set_pay_for_actual_work(month,
                                                 float(row[MonthHeaders.PAY_FOR_ACTUAL_WORK.value]))

                self.employee_data[personal_num] = employee

        return True

    def __set_year_and_quarter(self) -> None:
        """Set year and quarter of the report.

        Sets which year and quarter the report is being generated for inside the template
        :return: bool indicating success or failure
        """
        months: tuple[int, ...] = tuple(int(m.split("_")[0]) for
                                        m in self.data.sheet_names if "_" in m)
        if months is None:
            raise AppError(error_code=ErrNoEnum.ERR_WORKING_WITH_EXCEL,
                           error_message="Chyba během zpracování vstupního souboru, prosím "
                                         "zkontrolujte formát Excelu na vstupu programu.")

        self.__year = int(self.data.sheet_names[0].split("_")[1])

        match months:
            case Quarters.FIRST_QUARTER.value:
                self.__quarter = 1
                self.data_months = {MonthEnum.JAN.value : None,
                                    MonthEnum.FEB.value : None,
                                    MonthEnum.MAR.value : None}
            case Quarters.SECOND_QUARTER.value:
                self.__quarter = 2
                self.data_months = {MonthEnum.APR.value : None,
                                    MonthEnum.MAY.value : None,
                                    MonthEnum.JUN.value : None}
            case Quarters.THIRD_QUARTER.value:
                self.__quarter = 3
                self.data_months = {MonthEnum.JUL.value : None,
                                    MonthEnum.AUG.value : None,
                                    MonthEnum.SEP.value : None}
            case Quarters.FOURTH_QUARTER.value:
                self.__quarter = 4
                self.data_months = {MonthEnum.OCT.value : None,
                                    MonthEnum.NOV.value : None,
                                    MonthEnum.DEC.value : None}
            case _:
                raise AppError(
                    error_code=ErrNoEnum.ERR_WORKING_WITH_EXCEL,
                    error_message="Chyba během zpracovávání podkladů, zkontrolujte prosím, že v "
                                  "podkladovém Excelu máte pracovní listy pro jednotlivé měsíce "
                                  "kvartálu a list pro personalistiku.",
                )

        if self.__quarter is None or self.__year is None:
            raise AppError(
                error_code=ErrNoEnum.INTERNAL_ERROR,
                error_message="Vnitřní chyba programu, zkuste to prosím znovu",
            )

        self.template_manager.write_into_cell(sheet_name=TemplateSheetNames.INTRO_SHEET,
                                              value=self.__quarter,
                                              row=6,
                                              col=4)

        self.template_manager.write_into_cell(sheet_name=TemplateSheetNames.INTRO_SHEET,
                                              value=self.__year,
                                              row=6,
                                              col=9)

    def __save_processed(self, filename: str) -> bool:
        """Save Excel after having finished processing.

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

    def __construct_headers(self) -> tuple[tuple[str, ...], ...]:
        months: tuple[str, str, str] | None = None
        match self.__quarter:
            case 1:
                months = (MonthEnum.JAN.value,
                          MonthEnum.FEB.value,
                          MonthEnum.MAR.value)
            case 2:
                months = (MonthEnum.APR.value,
                          MonthEnum.MAY.value,
                          MonthEnum.JUN.value)
            case 3:
                months = (MonthEnum.JUL.value,
                          MonthEnum.AUG.value,
                          MonthEnum.SEP.value)
            case 4:
                months = (MonthEnum.OCT.value,
                          MonthEnum.NOV.value,
                          MonthEnum.DEC.value)

        if months is None:
            raise AppError(error_code=ErrNoEnum.INTERNAL_ERROR,
                           error_message="Vnitřní chyba programu.")

        return (
            (EmployeeSheetHeaders.BLANK.value, EmployeeSheetHeaders.SURNAME.value),
            (EmployeeSheetHeaders.BLANK.value, EmployeeSheetHeaders.FIRST_NAME.value),
            (EmployeeSheetHeaders.BLANK.value, EmployeeSheetHeaders.BIRTH_NUM.value),
            (EmployeeSheetHeaders.BLANK.value, EmployeeSheetHeaders.CONTRACT_START.value),
            (EmployeeSheetHeaders.BLANK.value, EmployeeSheetHeaders.CONTRACT_END.value),
            (EmployeeSheetHeaders.BLANK.value, EmployeeSheetHeaders.INSURANCE_COMPANY.value),
            (EmployeeSheetHeaders.BLANK.value,
             EmployeeSheetHeaders.DISABILITY_RECOGNITION_FROM.value),
            (EmployeeSheetHeaders.MONTH.value,
             EmployeeSheetHeaders.DISABILITY_RECOGNITION_TO.value),
            (months[0], EmployeeSheetHeaders.DISABILITY_STATUS.value),
            (months[0], EmployeeSheetHeaders.GROSS_PAY.value),
            (months[0], EmployeeSheetHeaders.INSURANCE_PAYMENT.value),
            (months[0], EmployeeSheetHeaders.EMPLOYEE_WORKED_THIS_MONTH.value),
            (months[1], EmployeeSheetHeaders.DISABILITY_STATUS.value),
            (months[1], EmployeeSheetHeaders.GROSS_PAY.value),
            (months[1], EmployeeSheetHeaders.INSURANCE_PAYMENT.value),
            (months[1], EmployeeSheetHeaders.EMPLOYEE_WORKED_THIS_MONTH.value),
            (months[2], EmployeeSheetHeaders.DISABILITY_STATUS.value),
            (months[2], EmployeeSheetHeaders.GROSS_PAY.value),
            (months[2], EmployeeSheetHeaders.INSURANCE_PAYMENT.value),
            (months[2], EmployeeSheetHeaders.EMPLOYEE_WORKED_THIS_MONTH.value),
        )
