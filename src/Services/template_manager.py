"""
This module contains the definition of the TamplateManager class, used to download and prep the
government ministry's Excel template
"""
import os
import re
import tempfile
import time
import zipfile
from pathlib import Path

import pandas as pd
import requests

from src.Enums.err_no_enum import ErrNoEnum
from src.Utils.error_handler import ErrorHandler


class TemplateManager:
    """
    This class handles downloading the template for the output Excel sheet, if it has already been
    downloaded previously,
    it does not download anything, using the already downloaded file
    """
    def __init__(self, template_url: str):
        self._url: str = template_url
        self._app_name: Path = Path("Dotacovatko")
        self.path: Path = self._get_writable_path()
        self.template: pd.ExcelFile | None = None
        self._work_sheets: dict[str, pd.DataFrame] | None = None

    def _get_writable_path(self) -> Path:
        """
        This method finds the best place to store the template file, it goes
        APPPDATA -> Documents -> system temp
        :return: filepath which will be written into
        """
        appdata: Path = os.environ.get("LOCALAPPDATA", "") / self._app_name
        documents: Path = Path("~").expanduser() / Path("Documents") / self._app_name
        system_temp: Path = Path(tempfile.gettempdir()) / self._app_name

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

    def _is_template_ready(self) -> bool:
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
        if self._is_template_ready():
            self._scrub_template()
            return True

        try:
            response = requests.get(self._url, timeout=5)
            response.raise_for_status()

            with self.path.open("wb") as file:
                file.write(response.content)

            return self._scrub_template()

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

    def _scrub_template(self) -> bool:
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
                        value: str | int | float,
                        row: int | None = None,
                        col: int | None = None,
                        row_header: str | tuple[str, str] | None = None,
                        col_header: str | tuple[str, str] | None = None) -> bool:
        """
        Method used for writing into a certain cell of the template
        :param sheet_name: sheet the cell is in
        :param value: value to put into the cell
        :param row: row the cell is in as an integer
        :param col: column the cell is in as an integer
        :param row_header: header of the row the cell is in, its key
        :param col_header: header of the column the cell is in, its key
        :return: boolean representing the success or failure of the write
        """
        try:
            sheet = self._get_sheet(sheet_name)

            row_idx = sheet.index(row) if row is not None else row_header
            col_idx = sheet.columns[col] if col is not None else col_header

            if row_idx is None or col_idx is None:
                ErrorHandler(error_code=ErrNoEnum.ERR_WORKING_WITH_EXCEL,
                             error_message="Interní chyba proramu, zkuste to prosím znovu.")
            sheet.at[row_idx, col_idx] = value

        except (IndexError, KeyError, TypeError, AttributeError):
            return False
        return True

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

            with pd.ExcelWriter(destination, engine="openpyxl") as writer:
                for sheet_name in self.template.sheet_names:
                    df = self._work_sheets.get(sheet_name)
                    if df is None:
                        df = self.template.parse(sheet_name)

                    df.to_excel(writer, sheet_name=sheet_name, index=False)

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
            self.template = pd.ExcelFile(path_or_buffer=self.path)
            return True
        except Exception:
            return False

    def _get_sheet(self, sheet_name: str) -> pd.DataFrame:
        """
        Internal helper method for getting the specified sheet from the internal work cache or
        parsing it from the ExcelFile if not yet loaded
        :param sheet_name: sheet to be retrieved
        :return: DataFrame of the sheet requested
        """
        if sheet_name not in self._work_sheets:
            self._work_sheets[sheet_name] = self.template.parse(sheet_name)

        return self._work_sheets[sheet_name]
