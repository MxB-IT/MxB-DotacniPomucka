import pandas as pd
from Enums import ErrNoEnum
from Services.TemplateManager import TemplateManager

from Utils.ErrorHandler import ErrorHandler


class ExcelProcessor:
    """
    Class made for handling loading and processing the Excel files
    """
    def __init__(self) -> None:
        self.file_path = None
        self.output_directory = None
        self.data = None
        self.template = None

    def set_input(self, file_path: str) -> bool:
        """
        This method sets the filepath to the input Excel file.
        :return: True if successful, False otherwise
        """
        try:
            self.file_path = file_path
            return True
        except Exception as e:
            ErrorHandler(error_code=ErrNoEnum.ERR_OPENING_EXCEL,
                         error_message=f"Chyba při otevírání Excel souboru, zkuste to prosím znovu\n"
                                       f"Chybový výstup:\n"
                                       f"{e}")
            return False

    def set_output_directory(self, output_directory: str) -> bool:
        """
        This method attempts to set the output directory for the modified Excel file
        :param output_directory: string indicating the filepath to the output directory
        :return: True if successful, False otherwise
        """
        try:
            self.output_directory = output_directory
            return True
        except Exception as e:
            ErrorHandler(error_code=ErrNoEnum.ERR_SELECTING_OUTPUT,
                         error_message=f"Chyba při volení složky pro výstup, zkuste to prosím znovu.\n"
                                       f"Chybový výstup:\n"
                                       f"{e}")
            return False

    def load_template(self) -> bool:
        """
        This method loads the template Excel file into a pandas dataframe in order to be edited
        :return: bool indicating if the template was successfully loaded
        """
        try:
            template_manager = TemplateManager(r"https://mpsv.gov.cz/cms/documents/57e12a5e-05b3-6511-0b8a-25dab64d5396/seznam%20zam%C4%9Bstnanc%C5%AF%20OZP_verze%2023_9_2025.xlsx")
        except PermissionError as e:
            ErrorHandler(error_code=ErrNoEnum.ERR_FAILED_TO_DOWNLOAD, error_message=str(e))
            return False

        if not template_manager.download_template():
            raise ConnectionError("Nepodařilo se stáhnout Excel šablonu MPSV, zkontrolujte připojení k internetu a zkuste to prosím znovu.")