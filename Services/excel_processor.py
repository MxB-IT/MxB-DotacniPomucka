import pandas as pd
from Enums import ErrNoEnum
from Services.template_manager import TemplateManager

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
        self.employee_data = []

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

        self.template = pd.read_excel(io=template_manager.path,
                                      header=[10, 11],
                                      thousands='.',
                                      decimal=',',
                                      sheet_name="2) seznam zaměstnanců OZP",
                                      engine="openpyxl")

        with open('output.txt', 'w', encoding='utf-8') as f:
            sheet_names = list(self.template.keys())
            f.write(f'Sheet name: {sheet_names[1]}')
            f.write("-" * 30 + '\n')
            f.write(self.template.to_string())

        return True

    def load_data(self, data_path: str) -> bool:
        """
        Loads an Excel file into a pandas dataframe in the data attribute
        :param data_path: path to the input Excel file
        :return: bool indicating success or failure
        """
        try:
            self.data = pd.read_excel(io=data_path,
                                      header=0,
                                      thousands='.',
                                      decimal=',',
                                      engine="openpyxl")
        except (IOError, OSError) as e:
            ErrorHandler(error_code=ErrNoEnum.ERR_OPENING_EXCEL,
                         error_message="Nepodařilo se otevřít Excel soubor, prosím ujistěte se, že jej nemáte nikde otevřený a zkuste to znovu.")
            return False
        return True

    def process_input_data(self) -> bool:
        """
        Processes the input Excel file and populates the template with data extracted from it
        :return: bool indicating success or failure
        """
        template_row = 0

        try:
            for employee, (idx, row) in zip(self.employee_data, self.template.iterrows()):
                employee_name: str = employee[0, "Jméno"]
                employee_surname: str = employee_name.split(sep=",")[0]
                employee_firstname: str = employee_name.split(sep=",")[1]

                self.template.at[idx, ("", "Příjmení")] = employee_surname
                self.template.at[idx, ("", "Jméno")] = employee_firstname

                self.template.at[idx, (self.template.columns[1][0], "Hrubá mzda / plat (v Kč)")] = employee["Součet hrubé mzdy a náhrady za nemoc"]

        except Exception as e:
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
        block_size = 6

        try:
            for i in range(0, len(self.data), block_size):
                chunk = self.data.iloc[i:i + block_size].copy()

                chunk.reset_index(drop=True,
                                  inplace=True)
                chunk.columns = self.data.columns

                self.employee_data.append(chunk)

        except Exception as e:
            ErrorHandler(error_code=ErrNoEnum.ERR_WORKING_WITH_EXCEL,
                         error_message="Chyba během zpracování Excelu, zkontrolujte, že máte správnou tabulku prosím")
            return False
        return True

