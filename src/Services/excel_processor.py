"""Contains the ExcelProcessor class used for processing the provided input Excel file."""
import multiprocessing as mp
import time
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from Enums import MonthEnum
from Enums.employee_data_headers import EmployeeDataHeaders
from Enums.employee_input_headers import EmployeeSheetHeaders
from Enums.err_no_enum import ErrNoEnum
from Enums.human_resources_headers import HumanResourcesHeaders
from Enums.month_headers import MonthHeaders
from Enums.quarters import Quarters
from Enums.queue_status import QueueStatus
from Enums.template_sheet_names import TemplateSheetNames
from Mappers.disability_type_mapper import DisabilityTypeMapper
from Mappers.insurance_company_mapper import InsuranceCompanyMapper
from Services.service_base import ServiceBase
from Services.template_manager import TemplateManager
from Utils.app_error import AppError
from Utils.error_handler import ErrorHandler


class ExcelProcessor(ServiceBase):
    """Class made for handling loading and processing the Excel files."""

    def __init__(self,
                 inbound_queue: mp.Queue[QueueStatus],
                 outbound_queue: mp.Queue[QueueStatus | AppError | float],
                 input_path: Path,
                 output_directory: Path,
                 ) -> None:
        """Initialise the ExcelProcessor.

        Initialises the ExcelProcessor, initialising all internal variables as blanks
        :param inbound_queue: Multiprocessing queue for inbound messages.
        :param outbound_queue: Multiprocessing queue for outbound messages.
        :param input_path: Path to the input Excel file.
        :param output_directory: Path to the directory to write the result into
        :return: None.
        """
        super().__init__(
            inbound_queue=inbound_queue,
            outbound_queue=outbound_queue,
        )

        self.__file_path: Path = input_path
        """
        Path leading to the input file, used to open the file and load data from it.
        :meta private:
        """

        self.__output_directory: Path = output_directory
        """
        Path leading to the output directory, used to write the result of the operation.
        :meta private:
        """

        self.__data: pd.ExcelFile
        """
        Attribute used to store the loaded data inside the object.
        :meta private:
        """

        self.__template_manager: TemplateManager
        """
        Attribute used to hold the reference to the template manager object, used to work with the downloaded template
        that this software is supposed to fill in.
        :meta private:
        """

        self.__employee_data: pd.DataFrame
        """
        Attribute used to hold the DataFrame with the unified and sorted employee data.
        :meta private:
        """

        self.__data_months: dict[str, pd.DataFrame | None] = {}
        """
        Attribute used to hold DataFrames with data from the month sheets, containing information about employee
        payrolls.
        :meta private:
        """

        self.__year: int
        """
        Attribute used to determine the year of the processed report.
        :meta private:
        """

        self.__quarter: int
        """
        Attribute used to determine the month of the processed report.
        :meta private:
        """

    def run(self) -> None:
        """Run the service.

        :return: None.
        """
        try:
            self.load_template()

            if self._stop_event.is_set():
                return

            self.load_data()

            if self._stop_event.is_set():
                return

            self.process_input_data()

        except AppError as e:
            self._send_msg(e)

        except Exception:
            self._send_msg(
                AppError(
                    error_code=ErrNoEnum.INTERNAL_ERROR,
                    error_message="Neznámá chyba, zkuste to prosím znovu.",
                ),
            )

    def load_template(self) -> None:
        """Load template Excel file via openpyxl.

        This method loads the template Excel file into a pandas dataframe in order to be edited,
        loads sheets that will be explicitly required into separate attributes
        :return: None, raises an error if failed
        """
        try:
            self.__template_manager = TemplateManager(r"https://mpsv.gov.cz/cms/documents/57e12a5e-05b3-6511-0b8a-25dab64d5396/seznam%20zam%C4%9Bstnanc%C5%AF%20OZP_verze%2023_9_2025.xlsx")
        except PermissionError as e:
            raise AppError(error_code=ErrNoEnum.ERR_FAILED_TO_DOWNLOAD,
                           error_message="Chyba při stahování souboru, program nemá"
                                         " dostatečná práva.") from e

        if not self.__template_manager.download_template():
            raise AppError(error_code=ErrNoEnum.ERR_FAILED_TO_DOWNLOAD,
                           error_message="Nepodařilo se stáhnout Excel šablonu MPSV, zkontrolujte"
                                         "připojení k internetu a zkuste to prosím znovu.")

        if not self.__template_manager.load_template_into_memory():
            raise AppError(error_code=ErrNoEnum.ERR_FAILED_TO_DOWNLOAD,
                           error_message="Nepodařilo se načíst šablonu, zkontrolujte, že je"
                                         " šablona v pořádku a zkuste to prosím znovu.")

    def load_data(self) -> None:
        """Load Excel file containing the data to process.

        Loads an Excel file into a pandas dataframe in the data attribute
        :return: None, raises an error if failed
        """
        try:
            self.__data = pd.ExcelFile(
                path_or_buffer=self.__file_path,
            )

        except OSError as e:
            raise AppError(error_code=ErrNoEnum.ERR_OPENING_EXCEL,
                           error_message="Nepodařilo se otevřít Excel soubor, prosím ujistěte se, "
                                         "že jej nemáte nikde otevřený a zkuste to znovu.") from e

    def process_input_data(self) -> None:
        """Process the input file.

        Processes the input Excel file and populates the template with data extracted from it.
        :return: None
        """
        self.__set_year_and_quarter()

        if self.__template_manager is None:
            raise AppError(
                error_code=ErrNoEnum.INTERNAL_ERROR,
                error_message="Interní chyba programu, zkuste to prosím znovu",
            )

        if not self.__template_manager.reload_template():
            raise AppError(
                error_code=ErrNoEnum.INTERNAL_ERROR,
                error_message="Chyba během znovunačítání Excelu",
            )

        if self.__data_months == {}:
            raise AppError(
                error_code=ErrNoEnum.ERR_WORKING_WITH_EXCEL,
                error_message="Chyba při zpracování vstupního Excelu, zkontrolujte prosím formát názvu listů v Excelu,"
                              ' korektní je: "[měsíc]_[rok]"',
            )

        headers: tuple[tuple[str, ...], ...] = self.__construct_headers()

        self.__template_manager.build_col_map(TemplateSheetNames.EMPLOYEE_LIST.value,
                                              headers)

        self.__process_employee_data()

        row: int = 13

        for _, employee_row in self.__employee_data.iterrows():
            if self._stop_event.is_set():
                return

            time.sleep(0.001)

            for month in self.__data_months:
                if self._stop_event.is_set():
                    return

                self.__template_manager.write_into_cell(
                    sheet_name=TemplateSheetNames.EMPLOYEE_LIST.value,
                    col_header=(
                        month,
                        EmployeeSheetHeaders.DISABILITY_STATUS.value,
                    ),
                    row=row,
                    value=employee_row[EmployeeDataHeaders.DISABILITY_STATUS.value],
                )
                self.__template_manager.write_into_cell(
                    sheet_name=TemplateSheetNames.EMPLOYEE_LIST.value,
                    col_header=(
                        month.upper(),
                        EmployeeSheetHeaders.GROSS_PAY.value,
                    ),
                    row=row,
                    value=employee_row[f"{EmployeeDataHeaders.GROSS_PAY.value}_{MonthEnum(month)}"],
                )
                self.__template_manager.write_into_cell(
                    sheet_name=TemplateSheetNames.EMPLOYEE_LIST.value,
                    col_header=(
                        month.upper(),
                        EmployeeSheetHeaders.INSURANCE_PAYMENT.value,
                    ),
                    row=row,
                    value=employee_row[f"{EmployeeDataHeaders.INSURANCE_PAYMENT.value}_{MonthEnum(month)}"],
                )
                self.__template_manager.write_into_cell(
                    sheet_name=TemplateSheetNames.EMPLOYEE_LIST.value,
                    col_header=(
                        month.upper(),
                        EmployeeSheetHeaders.EMPLOYEE_WORKED_THIS_MONTH.value,
                    ),
                    row=row,
                    value=employee_row[f"{EmployeeDataHeaders.EMPLOYEE_WORKED.value}_{MonthEnum(month)}"],
                )

            self.__template_manager.write_into_cell(
                sheet_name=TemplateSheetNames.EMPLOYEE_LIST.value,
                col_header=(
                    EmployeeSheetHeaders.BLANK.value,
                    EmployeeSheetHeaders.FIRST_NAME.value,
                ),
                row=row,
                value=employee_row[EmployeeDataHeaders.FIRST_NAME],
            )
            self.__template_manager.write_into_cell(
                sheet_name=TemplateSheetNames.EMPLOYEE_LIST.value,
                col_header=(
                    EmployeeSheetHeaders.BLANK.value,
                    EmployeeSheetHeaders.SURNAME.value,
                ),
                row=row,
                value=employee_row[EmployeeDataHeaders.SURNAME],
            )
            self.__template_manager.write_into_cell(
                sheet_name=TemplateSheetNames.EMPLOYEE_LIST.value,
                col_header=(
                    EmployeeSheetHeaders.BLANK.value,
                    EmployeeSheetHeaders.BIRTH_NUM.value,
                ),
                row=row,
                value=employee_row[EmployeeDataHeaders.BIRTH_NUM],
            )
            self.__template_manager.write_into_cell(
                sheet_name=TemplateSheetNames.EMPLOYEE_LIST.value,
                col_header=(
                    EmployeeSheetHeaders.BLANK.value,
                    EmployeeSheetHeaders.CONTRACT_START.value,
                ),
                row=row,
                value=employee_row[EmployeeDataHeaders.CONTRACT_START_DATE],
            )
            self.__template_manager.write_into_cell(
                sheet_name=TemplateSheetNames.EMPLOYEE_LIST.value,
                col_header=(
                    EmployeeSheetHeaders.BLANK.value,
                    EmployeeSheetHeaders.CONTRACT_END.value,
                ),
                row=row,
                value=employee_row[EmployeeDataHeaders.CONTRACT_END_DATE],
            )
            self.__template_manager.write_into_cell(
                sheet_name=TemplateSheetNames.EMPLOYEE_LIST.value,
                col_header=(
                    EmployeeSheetHeaders.BLANK.value,
                    EmployeeSheetHeaders.INSURANCE_COMPANY.value,
                ),
                row=row,
                value=employee_row[EmployeeDataHeaders.INSURANCE_CODE],
            )
            self.__template_manager.write_into_cell(
                sheet_name=TemplateSheetNames.EMPLOYEE_LIST.value,
                col_header=(
                    EmployeeSheetHeaders.BLANK.value,
                    EmployeeSheetHeaders.DISABILITY_RECOGNITION_FROM.value,
                ),
                row=row,
                value=employee_row[EmployeeDataHeaders.DISABILITY_RECOGNISED_FROM],
            )
            self.__template_manager.write_into_cell(
                sheet_name=TemplateSheetNames.EMPLOYEE_LIST.value,
                col_header=(
                    "Měsíc:",
                    EmployeeSheetHeaders.DISABILITY_RECOGNITION_TO.value,
                ),
                row=row,
                value=employee_row[EmployeeDataHeaders.DISABILITY_RECOGNISED_TO],
            )

            row += 1

        self.__save_processed(f"{self.__quarter}Q{self.__year}seznam+zaměstnanců+OZP.xlsx")
        self._send_msg(QueueStatus.SUCCESS)

    def __process_employee_data(self) -> None:
        """Process employee data and create Employee objects representing them.

        Processes employee data in the input sheet and inputs them into the template.
        :return: None.
        """
        if self.__data is None:
            raise AppError(error_code=ErrNoEnum.INTERNAL_ERROR,
                           error_message="Interní chyba programu")

        month_dataframes: list[pd.DataFrame] = [
            pd.read_excel(
                self.__data,
                self.__data.sheet_names[0],
            ),
            pd.read_excel(
                self.__data,
                self.__data.sheet_names[1],
            ),
            pd.read_excel(
                self.__data,
                self.__data.sheet_names[2],
            ),
        ]

        month_dataframes = [month.set_index(EmployeeSheetHeaders.PERSONAL_NUM.value) for month in month_dataframes]

        human_resources: pd.DataFrame = pd.read_excel(
            self.__data,
            self.__data.sheet_names[3],
        )

        human_resources = human_resources.set_index(HumanResourcesHeaders.PERSONAL_NUM.value)

        keys: list[str] = list(self.__data_months.keys())

        grouped_employees_df: pd.DataFrame = pd.concat(
            month_dataframes,
            axis=1,
            keys=keys,
        )

        human_resources.columns = pd.MultiIndex.from_product(
            [["HR"], human_resources.columns],
        )

        grouped_employees_df = grouped_employees_df.join(
            human_resources,
            how="inner",
        )

        start_dates: pd.DataFrame | pd.Series[Any] = grouped_employees_df.xs(
            MonthHeaders.CONTRACT_START.value,
            level=1,
            axis="columns",
            drop_level=False,
        )

        if isinstance(start_dates, pd.Series):
            start_dates = start_dates.bfill().iloc[0]
        else:
            start_dates = start_dates.bfill(
                axis="columns",
            ).iloc[:, 0]

        end_dates: pd.DataFrame | pd.Series[Any] = grouped_employees_df.xs(
            MonthHeaders.CONTRACT_END.value,
            level=1,
            axis=1,
            drop_level=False,
        )

        if isinstance(end_dates, pd.Series):
            end_dates = end_dates.bfill().iloc[0]
        else:
            end_dates = end_dates.bfill(
                axis="columns",
            ).iloc[:, 0]

        if self._stop_event.is_set():
            return

        self.__employee_data = pd.DataFrame(
            data={
                EmployeeDataHeaders.SURNAME: grouped_employees_df[
                    ("HR", HumanResourcesHeaders.SURNAME.value)
                ],
                EmployeeDataHeaders.FIRST_NAME: grouped_employees_df[
                    ("HR", HumanResourcesHeaders.FIRST_NAME.value)
                ],
                EmployeeDataHeaders.BIRTH_NUM: grouped_employees_df[
                    ("HR", HumanResourcesHeaders.BIRTH_NUM.value)
                ],
                EmployeeDataHeaders.CONTRACT_START_DATE: start_dates,
                EmployeeDataHeaders.CONTRACT_END_DATE: end_dates,
                EmployeeDataHeaders.INSURANCE_CODE: grouped_employees_df[
                    ("HR", HumanResourcesHeaders.INSURANCE_COMPANY.value)
                ],
                EmployeeDataHeaders.DISABILITY_RECOGNISED_FROM: grouped_employees_df[
                    ("HR", HumanResourcesHeaders.DISABILITY_START.value)
                ],
                EmployeeDataHeaders.DISABILITY_RECOGNISED_TO: pd.NaT,
                EmployeeDataHeaders.DISABILITY_STATUS: grouped_employees_df[
                    ("HR", HumanResourcesHeaders.DISABILITY_STATUS.value)
                ],
                f"{EmployeeDataHeaders.GROSS_PAY.value}_{MonthEnum(keys[0])}": np.where(
                    grouped_employees_df[(keys[0], MonthHeaders.GROSS_PAY.value)].isna(),
                    0,
                    grouped_employees_df[(keys[0], MonthHeaders.GROSS_PAY.value)],
                ),
                f"{EmployeeDataHeaders.GROSS_PAY.value}_{MonthEnum(keys[1])}": np.where(
                    grouped_employees_df[(keys[1], MonthHeaders.GROSS_PAY.value)].isna(),
                    0,
                    grouped_employees_df[(keys[1], MonthHeaders.GROSS_PAY.value)],
                ),
                f"{EmployeeDataHeaders.GROSS_PAY.value}_{MonthEnum(keys[2])}": np.where(
                    grouped_employees_df[(keys[2], MonthHeaders.GROSS_PAY.value)].isna(),
                    0,
                    grouped_employees_df[(keys[2], MonthHeaders.GROSS_PAY.value)],
                ),
                f"{EmployeeDataHeaders.PAY_FOR_ACTUAL_WORK.value}_{MonthEnum(keys[0])}": np.where(
                    grouped_employees_df[(keys[0], MonthHeaders.PAY_FOR_ACTUAL_WORK.value)].isna(),
                    0,
                    grouped_employees_df[(keys[0], MonthHeaders.PAY_FOR_ACTUAL_WORK.value)],
                ),
                f"{EmployeeDataHeaders.PAY_FOR_ACTUAL_WORK.value}_{MonthEnum(keys[1])}": np.where(
                    grouped_employees_df[(keys[1], MonthHeaders.PAY_FOR_ACTUAL_WORK.value)].isna(),
                    0,
                    grouped_employees_df[(keys[1], MonthHeaders.PAY_FOR_ACTUAL_WORK.value)],
                ),
                f"{EmployeeDataHeaders.PAY_FOR_ACTUAL_WORK.value}_{MonthEnum(keys[2])}": np.where(
                    grouped_employees_df[(keys[2], MonthHeaders.PAY_FOR_ACTUAL_WORK.value)].isna(),
                    0,
                    grouped_employees_df[(keys[2], MonthHeaders.PAY_FOR_ACTUAL_WORK.value)],
                ),
                f"{EmployeeDataHeaders.INSURANCE_PAYMENT.value}_{MonthEnum(keys[0])}": np.where(
                    (grouped_employees_df[(keys[0], MonthHeaders.COMPANY_INSURANCE.value)].isna()) &
                    (grouped_employees_df[(keys[0], MonthHeaders.COMPANY_SOCIAL_SEC.value)].isna()),
                    0,
                    grouped_employees_df[(keys[0], MonthHeaders.COMPANY_INSURANCE.value)] +
                    grouped_employees_df[(keys[0], MonthHeaders.COMPANY_SOCIAL_SEC.value)],
                ),
                f"{EmployeeDataHeaders.INSURANCE_PAYMENT.value}_{MonthEnum(keys[1])}": np.where(
                    (grouped_employees_df[(keys[1], MonthHeaders.COMPANY_INSURANCE.value)].isna()) &
                    (grouped_employees_df[(keys[1], MonthHeaders.COMPANY_SOCIAL_SEC.value)].isna()),
                    0,
                    grouped_employees_df[(keys[1], MonthHeaders.COMPANY_INSURANCE.value)] +
                    grouped_employees_df[(keys[1], MonthHeaders.COMPANY_SOCIAL_SEC.value)],
                ),
                f"{EmployeeDataHeaders.INSURANCE_PAYMENT.value}_{MonthEnum(keys[2])}": np.where(
                    (grouped_employees_df[(keys[2], MonthHeaders.COMPANY_INSURANCE.value)].isna()) &
                    (grouped_employees_df[(keys[2], MonthHeaders.COMPANY_SOCIAL_SEC.value)].isna()),
                    0,
                    grouped_employees_df[(keys[2], MonthHeaders.COMPANY_INSURANCE.value)] +
                    grouped_employees_df[(keys[2], MonthHeaders.COMPANY_SOCIAL_SEC.value)],
                ),
            },
        )

        if self._stop_event.is_set():
            return

        self.__employee_data[EmployeeDataHeaders.DISABILITY_STATUS] = self.__employee_data[
            EmployeeDataHeaders.DISABILITY_STATUS
        ].map(
            DisabilityTypeMapper.from_int,
        )

        self.__employee_data[EmployeeDataHeaders.INSURANCE_CODE] = self.__employee_data[
            EmployeeDataHeaders.INSURANCE_CODE
        ].map(
            InsuranceCompanyMapper.from_str,
        )

        for key in keys:
            if self._stop_event.is_set():
                return

            self.__employee_data[f"{EmployeeDataHeaders.EMPLOYEE_WORKED}_{MonthEnum(key)}"] = (
                self.__employee_data[
                    f"{EmployeeDataHeaders.PAY_FOR_ACTUAL_WORK.value}_{MonthEnum(key)}"
                ]
                > 0
            ).astype(int)

        self.__employee_data = self.__employee_data[
            (
                self.__employee_data[
                    f"{EmployeeDataHeaders.EMPLOYEE_WORKED.value}_{MonthEnum(keys[0])}"
                ]
                != 0
            )
            | (
                self.__employee_data[
                    f"{EmployeeDataHeaders.EMPLOYEE_WORKED.value}_{MonthEnum(keys[1])}"
                ]
                != 0
            )
            | (
                self.__employee_data[
                    f"{EmployeeDataHeaders.EMPLOYEE_WORKED.value}_{MonthEnum(keys[2])}"
                ]
                != 0
            )
            | (
                self.__employee_data[
                    f"{EmployeeDataHeaders.GROSS_PAY.value}_{MonthEnum(keys[0])}"
                ]
                != 0
            )
            | (
                self.__employee_data[
                    f"{EmployeeDataHeaders.GROSS_PAY.value}_{MonthEnum(keys[1])}"
                ]
                != 0
            )
            | (
                self.__employee_data[
                    f"{EmployeeDataHeaders.GROSS_PAY.value}_{MonthEnum(keys[2])}"
                ]
                != 0
            )
        ]

        return

    def __set_year_and_quarter(self) -> None:
        """Set year and quarter of the report.

        Sets which year and quarter the report is being generated for inside the template
        :return: bool indicating success or failure
        """
        if self._stop_event.is_set():
            return

        if any(isinstance(month, int) for month in self.__data.sheet_names):
            raise AppError(
                error_code=ErrNoEnum.ERR_WORKING_WITH_EXCEL,
                error_message="Chyba při práci s Excelem, prosím zkontrolujte, že vstupní Excel má správně pojmenované "
                              "listy (ve formátu [měsíc_rok] pro listy s daty ohledně aktivity zaměstnanců v měsíci a "
                              '"personalistika" pro list personalistika)',
            )

        months: tuple[int, ...] = tuple(int(m.split("_")[0]) for
                                        m in self.__data.sheet_names if "_" in m)
        if months is None:
            raise AppError(error_code=ErrNoEnum.ERR_WORKING_WITH_EXCEL,
                           error_message="Chyba během zpracování vstupního souboru, prosím "
                                         "zkontrolujte formát Excelu na vstupu programu.")

        self.__year = int(self.__data.sheet_names[0].split("_")[1])

        match months:
            case Quarters.FIRST_QUARTER.value:
                self.__quarter = 1
                self.__data_months = {MonthEnum.JAN.value : None,
                                      MonthEnum.FEB.value : None,
                                      MonthEnum.MAR.value : None}
            case Quarters.SECOND_QUARTER.value:
                self.__quarter = 2
                self.__data_months = {MonthEnum.APR.value : None,
                                      MonthEnum.MAY.value : None,
                                      MonthEnum.JUN.value : None}
            case Quarters.THIRD_QUARTER.value:
                self.__quarter = 3
                self.__data_months = {MonthEnum.JUL.value : None,
                                      MonthEnum.AUG.value : None,
                                      MonthEnum.SEP.value : None}
            case Quarters.FOURTH_QUARTER.value:
                self.__quarter = 4
                self.__data_months = {MonthEnum.OCT.value : None,
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

        self.__template_manager.write_into_cell(sheet_name=TemplateSheetNames.INTRO_SHEET,
                                                value=self.__quarter,
                                                row=6,
                                                col=4)

        self.__template_manager.write_into_cell(sheet_name=TemplateSheetNames.INTRO_SHEET,
                                                value=self.__year,
                                                row=6,
                                                col=9)

    def __save_processed(self, filename: str) -> bool:
        """Save Excel after having finished processing.

        Saves the processed data into an Excel file with a specified filename
        :param filename: desired name of the output file
        :return: bool indicating success or failure
        """
        if not self.__output_directory:
            ErrorHandler(error_code=ErrNoEnum.ERR_FAILED_TO_SAVE,
                         error_message="Složka pro výstup nebyla nastavena, zkuste to "
                                       "prosím znovu.")
            return False

        final_path: Path = self.__output_directory / filename

        if final_path.suffix != ".xlsx":
            final_path = final_path.with_suffix(".xlsx")

        return self.__template_manager.write_file(final_path)

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
