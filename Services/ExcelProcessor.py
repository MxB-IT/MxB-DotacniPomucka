import pandas as pd
from Enums import ErrNoEnum

from Utils.ErrorHandler import ErrorHandler


class ExcelProcessor:
    """
    Class made for handling loading and processing the Excel files
    """
    def __init__(self) -> None:
        self.file_path = None
        self.output_directory = None
        self.data = None

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
                         error_message=f"Chyba při volení složky pro výstup, zkuste to prosím znovu\n"
                                       f"Chybový výstup:\n"
                                       f"{e}")
            return False