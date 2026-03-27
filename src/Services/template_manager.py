"""
This module contains the definition of the TamplateManager class, used to download and prep the
government ministry's Excel template
"""
import os
import re
import tempfile
import time
import zipfile
from datetime import datetime
from enum import Enum
from pathlib import Path

import openpyxl
import requests

from src.Enums import MonthEnum, TemplateSheetNames
from src.Enums.employee_sheet_headers import EmployeeSheetHeaders
from src.Enums.err_no_enum import ErrNoEnum
from src.Utils.error_handler import ErrorHandler


class TemplateManager:
    """
    This class handles downloading the template for the output Excel sheet, if it has already been
    downloaded previously,
    it does not download anything, using the already downloaded file
    """
    def __init__(self, template_url: str):
        self.__url: str = template_url
        self.__app_name: Path = Path("Dotacovatko")
        self.path: Path = self.__get_writable_path()
        self.template: openpyxl.Workbook | None = None
        self.__col_mapping: dict[tuple[str, tuple[str, str]], int] = {}

    def __get_writable_path(self) -> Path:
        """
        This method finds the best place to store the template file, it goes
        APPPDATA -> Documents -> system temp
        :return: filepath which will be written into
        """
        appdata: Path = os.environ.get("LOCALAPPDATA", "") / self.__app_name
        documents: Path = Path("~").expanduser() / Path("Documents") / self.__app_name
        system_temp: Path = Path(tempfile.gettempdir()) / self.__app_name

        for path in [appdata, documents, system_temp]:
            try:
                Path.mkdir(path, exist_ok=True)
                test_file: Path = path / Path("permsTest")
                with test_file.open("w") as f:
                    f.write("test")
                test_file.unlink()

                return path / Path(f"MPSV_Template_{time.strftime('%Y')}.xlsx")
            except OSError:
                continue

        raise PermissionError("Aplikace nebyla schopna najít složku, do které by mohla stáhnout a "
                              "uložit Excel MPSV.")

    def __is_template_ready(self) -> bool:
        """
        Checks whether the template has already been downloaded
        :return: True if it has already been downloaded, False otherwise
        """
        return self.path.exists()

    def download_template(self) -> bool:
        """
        Downloads the template file from the URL and stores it in the specified filepath
        :return: True if the download succeeds, false otherwise
        """
        if self.__is_template_ready():
            self.__scrub_template()
            return True

        try:
            response = requests.get(self.__url, timeout=5)
            response.raise_for_status()

            with self.path.open("wb") as file:
                file.write(response.content)

            return self.__scrub_template()

        except requests.exceptions.Timeout:
            ErrorHandler(
                error_code=ErrNoEnum.ERR_FAILED_TO_DOWNLOAD,
                error_message="Chyba při stahování šablony, ujistěte se prosím, že jste "
                "připojeni k internetu a zkuste to znovu",
            )
            return False

        except requests.exceptions.HTTPError:
            ErrorHandler(
                error_code=ErrNoEnum.ERR_FAILED_TO_DOWNLOAD,
                error_message="Chyba při stahování šablony, ujistěte se prosím, že vládní stránky"
                "momentálně fungují a zkuste to prosím znovu",
            )
            return False

        except requests.exceptions.RequestException:
            ErrorHandler(
                error_code=ErrNoEnum.ERR_FAILED_TO_DOWNLOAD,
                error_message="Chyba při stahování šablony, zkuste to prosím znovu",
            )
            return False

    def __scrub_template(self) -> bool:
        """
        Removes certain metadata from the template that caused an error when opening
        :return: bool indicating success or failure
        """
        temp_file: Path = self.path.with_suffix(".tmp")

        try:
            with zipfile.ZipFile(self.path, "r") as zin, zipfile.ZipFile(temp_file, "w") as zout:
                for item in zin.infolist():
                    data = zin.read(item.filename)

                    if item.filename == "xl/workbook.xml":
                        xml_content = data.decode("utf-8")
                        xml_content = re.sub(r"<definedNames>.*?</definedNames>",
                                             "",
                                             xml_content,
                                             flags=re.DOTALL)
                        data = xml_content.encode("utf-8")

                    zout.writestr(item, data)

            temp_file.replace(self.path)
            return True
        except (FileNotFoundError, PermissionError, OSError,
                zipfile.BadZipFile, zipfile.LargeZipFile):
            if temp_file.exists():
                temp_file.unlink()

            ErrorHandler(error_code=ErrNoEnum.ERR_FAILED_TO_DOWNLOAD,
                         error_message="Chyba při načítání šablony, zkuste to prosím znovu")
            return False

    def write_into_cell(self, sheet_name: str,
                        value: str | int | float | datetime,
                        row: int,
                        col: int | None = None,
                        col_header: str | tuple[str, str] | None = None) -> bool:
        """
        Method used for writing into a certain cell of the template
        :param sheet_name: sheet the cell is in
        :param value: value to put into the cell
        :param row: row the cell is in as an integer
        :param col: column the cell is in as an integer
        :param col_header: header of the column the cell is in, its key
        :return: boolean representing the success or failure of the write
        """
        try:
            sheet = self.template[sheet_name]

            if col_header:
                col = self.__col_mapping.get((sheet_name, col_header))

            if row is None or col is None:
                ErrorHandler(error_code=ErrNoEnum.ERR_WORKING_WITH_EXCEL,
                             error_message="Interní chyba proramu, zkuste to prosím znovu.")
            sheet.cell(row, col).value = value

            return True

        except (IndexError, KeyError, TypeError, AttributeError):
            return False

    def write_file(self, destination: Path) -> bool:
        """
        Writes the processed template to a file, to the location specified by the destination param
        :param destination: Path representation of the folder to write into
        :return: bool, indicating success or failure of the write
        """
        if self.template is None:
            return False

        try:
            destination.parent.mkdir(parents=True, exist_ok=True)
            self.template.save(destination)

            return True

        except (PermissionError, OSError):
            ErrorHandler(error_code=ErrNoEnum.ERR_WORKING_WITH_EXCEL,
                         error_message="Zpracovaný soubor se nepodařilo uložit!")
            return False

    def load_template_into_memory(self) -> bool:
        """
        Loads the downloaded template into memory, like a good TemplateManager should
        :return: bool indicating success or failure of the load
        """
        try:
            self.template = openpyxl.load_workbook(filename=self.path,
                                                   data_only=False)

            self.__build_col_map(sheet_name=TemplateSheetNames.EMPLOYEE_LIST,
                                 first_level=MonthEnum,
                                 second_level=EmployeeSheetHeaders)
            return True
        except Exception:
            return False

    def __build_col_map(self,
                        sheet_name: str,
                        first_level: type[Enum],
                        second_level: type[Enum]) -> None:
        """
        Builds the column map for openpyxl to later use when writing into the template
        :param sheet_name: sheet for which the column map is to be built
        :param first_level: first index of the multiIndex value
        :param second_level: second index of the multiIndex value
        :return:
        """
        ws = self.template[sheet_name]

        current_level1: str = ""
        found: bool = False

        for second_level_val in second_level:
            print(second_level_val.value)
            for first_level_val in first_level:
                for row in range(1, ws.max_row):
                    for col in range(1, ws.max_column + 1):
                        level1 = ws.cell(row=row, column=col).value
                        level2 = ws.cell(row=row + 1, column=col).value or ""

                        if level1 is None:
                            if first_level_val == MonthEnum.BLANK:
                                current_level1 = ""
                            else:
                                continue

                        else:
                            current_level1 = level1

                        if row == 11:
                            print(
                                f"level1={current_level1}, level2={level2}\nfirst_val={first_level_val.value}, second_val={second_level_val.value}\nrow={row}, col={col}\nmap={self.__col_mapping}"
                            )

                        if current_level1 == first_level_val.value and level2 == second_level_val.value:
                            self.__col_mapping[sheet_name, (current_level1, level2)] = col
                            found = True
                            print("1st break")
                            break

                    if found:
                        print("2nd break")
                        break
                if found:
                    print("3rd break")
                    found = False
                    break
