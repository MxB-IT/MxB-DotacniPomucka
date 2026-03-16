"""
This module contains the ExcelProcessor class used for processing the provided input Excel file
"""
from pathlib import Path

import pandas as pd

from src.Enums.err_no_enum import ErrNoEnum
from src.Services.template_manager import TemplateManager
from src.Utils.error_handler import ErrorHandler


class ExcelProcessor:
    """
    Class made for handling loading and processing the Excel files
    """
    def __init__(self) -> None:
        self.file_path = None
        self.output_directory = None
        self.data = None
        self.template = None
        self.employee_data = []
        self.template_intro_sheet = None
        self.template_employee_sheet = None

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
            template_manager = TemplateManager(r"https://mpsv.gov.cz/cms/documents/57e12a5e-05b3-6511-0b8a-25dab64d5396/seznam%20zam%C4%9Bstnanc%C5%AF%20OZP_verze%2023_9_2025.xlsx")
        except PermissionError as e:
            ErrorHandler(error_code=ErrNoEnum.ERR_FAILED_TO_DOWNLOAD, error_message=str(e))
            return False

        if not template_manager.download_template():
            raise ConnectionError("Nepodařilo se stáhnout Excel šablonu MPSV, zkontrolujte"
                                  "připojení k internetu a zkuste to prosím znovu.")

        self.template = pd.read_excel(io=template_manager.path,
                                      header=[10, 11],
                                      thousands=".",
                                      decimal=",",
                                      sheet_name=None,
                                      engine="openpyxl")

        self.template_intro_sheet = self.template["1) Úvodní list"]
        self.template_employee_sheet =self.template["2) seznam zaměstnanců OZP"]

        with Path("output.txt").open(mode="w", encoding="utf-8") as f:
            sheet_names = list(self.template.keys())
            f.write(f"Sheet name: {sheet_names[1]}")
            f.write("-" * 30 + "\n")
            f.write(self.template.to_string())

        return True

    def load_data(self) -> bool:
        """
        Loads an Excel file into a pandas dataframe in the data attribute
        :return: bool indicating success or failure
        """
        try:
            self.data = pd.read_excel(io=self.file_path,
                                      header=0,
                                      thousands=".",
                                      decimal=",",
                                      engine="openpyxl",
                                      sheet_name=None)
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
        try:
            for employee, (idx, _row) in zip(self.employee_data,
                                            self.template.iterrows(),
                                            strict=False):
                employee_name: str = employee[0, "Jméno"]
                employee_surname: str = employee_name.split(sep=",")[0]
                employee_firstname: str = employee_name.split(sep=",")[1]

                self.template.at[idx, ("", "Příjmení")] = employee_surname
                self.template.at[idx, ("", "Jméno")] = employee_firstname

                self.template.at[idx, (self.template.columns[1][0], "Hrubá mzda / plat (v Kč)")] =\
                    employee["Součet hrubé mzdy a náhrady za nemoc"]

        except (IndexError, KeyError, TypeError):
            ErrorHandler(error_code=ErrNoEnum.ERR_WORKING_WITH_EXCEL,
                         error_message="Chyba během zpracovávání Excelu, zkuste to prosím znovu")
            return False
        return True

    def _clean_indexing(self):
        self.template.columns = pd.MultiIndex.from_tuples(
            [("" if "Unnamed" in a else a, b) for a, b in self.template.columns]
        )

    def _prepare_employee_data(self) -> bool:
        """
        Prepares employee data in the input sheet into a better format to work with
        :return: bool indicating success or failure
        """
        return True

    def _set_year_and_quarter(self) -> bool:
        """
        Sets which year and quarter the report is being generated for inside the template
        :return: bool indicating success or failure
        """
        return True

