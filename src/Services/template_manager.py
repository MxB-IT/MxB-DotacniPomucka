"""
This module contains the definition of the TamplateManager class, used to download and prep the
government ministry's Excel template
"""
import io
import os
import re
import tempfile
import time
import zipfile
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any

import openpyxl
import requests
import xlwings as xw
from openpyxl.cell import Cell, MergedCell
from openpyxl.workbook import Workbook
from openpyxl.worksheet.worksheet import Worksheet

from src.Enums.disability_status_enum import DisabilityStatus
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
        self.__col_mapping: dict[tuple[str, tuple[str, ...]], int] = {}

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
        try:
            # 1. Read the original into memory
            with self.path.open("rb") as f:
                original_data = f.read()

            in_buffer = io.BytesIO(original_data)
            out_buffer = io.BytesIO()

            with zipfile.ZipFile(in_buffer, "r") as zin:
                with zipfile.ZipFile(out_buffer, "w") as zout:
                    for item in zin.infolist():
                        # Read the raw content
                        content = zin.read(item.filename)

                        if item.filename == "xl/workbook.xml":
                            # Perform the scrub
                            # This regex is very specific to ensure we don't break the XML structure
                            pattern = rb"<definedName [^>]*>#N/A</definedName>"
                            if re.search(pattern, content):
                                content = re.sub(pattern, b"", content)

                        # CRITICAL: We create a new ZipInfo to reset the CRC/Size
                        # BUT we copy the compression type from the original item
                        new_item = zipfile.ZipInfo(item.filename)
                        new_item.compress_type = item.compress_type
                        new_item.create_system = item.create_system

                        # Write it back using the original compression method
                        zout.writestr(new_item, content)

            # 2. Check the size again. A small drop (bytes) is fine.
            # A 1MB drop means we failed to copy a folder.
            final_bytes = out_buffer.getvalue()

            # If it's still way smaller, the ZIP library is failing to see some parts.
            print(f"Original size: {len(original_data)} | New size: {len(final_bytes)}")

            with self.path.open("wb") as f:
                f.write(final_bytes)

            return True

        except Exception as e:
            print(f"Patching failed: {e}")
            return False

    def write_into_cell(self,
                        sheet_name: str,
                        value: str | int | float | datetime | DisabilityStatus,
                        row: int,
                        col: int | None = None,
                        col_header: str | tuple[str, ...] | None = None) -> bool:
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
                if isinstance(col_header, (str, Enum)):
                    lookup_header = (str(col_header).strip(),)
                else:
                    lookup_header = tuple(str(h).strip() for h in col_header)

                col = self.__col_mapping[(sheet_name, lookup_header)]

            if row is None or col is None:
                ErrorHandler(error_code=ErrNoEnum.INTERNAL_ERROR,
                             error_message="Interní chyba programu, zkuste to prosím znovu.")
                return False
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

            return True
        except Exception as e:
            print(f"Failed, {e}")
            return False

    def build_col_map(self,
                      sheet_name: str,
                      headers: tuple[tuple[str, ...], ...],
                      max_row: int = 30) -> None:
        """
        Builds the column map for openpyxl to later use when writing into the template
        :param sheet_name: sheet for which the column map is to be built
        :param headers: headers of the columns to be found
        :param max_row: maximum row to search for headers
        :return:
        """
        temp: Workbook = openpyxl.load_workbook(filename=self.path,data_only=True)
        ws = temp[sheet_name]

        for header in headers:
            col: int | None = self.__find_column_by_header(ws=ws,
                                                           header=header,
                                                           max_row=max_row)

            if col:
                self.__col_mapping[(sheet_name, header)] = col
                #print(self.__col_mapping)
            else:
                print(f"well, fuck, {header}")

        temp.close()



    def __find_column_by_header(self,
                                ws: Worksheet,
                                header: str | tuple | Enum,
                                max_row: int) -> int | None:
        """
        Locates a column by the header (or headers in the case of a multiIndex sheet) provided
        :param ws: worksheet to search
        :param header: header to look out for
        :return: int if it finds the column successfully, None otherwise
        """
        if isinstance(header, Enum):
            search_terms = (str(header.value).strip(),)
        elif isinstance(header, str):
            search_terms = (header.strip(),)
        else:
            search_terms = tuple(str(item).strip() for item in header)

        depth = len(search_terms)

        for col in range(1, ws.max_column + 1):
            for row in range(1, max_row):

                actual_headers = tuple(
                    str(self.__get_cell_value(ws=ws,
                                              row=row+i,
                                              col=col) or "").strip() for i in range(depth)
                )

                if actual_headers == search_terms:
                    return col

        return None

    def reload_template(self) -> bool:
        """
        Saves the loaded template workbook back onto the disk and forces the formulas inside to run
        and update the sheets accordingly
        """
        try:
            print(f"reloading, {self.path}")
            self.template.save(self.path)

            with xw.App(visible=False) as app:
                book = xw.Book(self.path)
                app.calculate()
                book.save()
                book.close()

            self.template = openpyxl.load_workbook(self.path,
                                                   data_only=False)
            return True
        except (PermissionError, OSError):
            ErrorHandler(error_code=ErrNoEnum.ERR_WORKING_WITH_EXCEL,
                         error_message="TODO")
            return False

    @staticmethod
    def __get_cell_value(ws: Worksheet, row: int, col: int) -> Any:
        """
        Defines logic for getting the value of a cell, custom logic is required to handle merged
        cells
        :param ws: worksheet in which the cell is located
        :param row: row of the cell
        :param col: column of the cell
        :return: Whatever the cell contains
        """
        cell: Cell | MergedCell = ws.cell(row=row, column=col)

        for merged_range in ws.merged_cells.ranges:
            if cell.coordinate in merged_range:
                return_val: Any = ws.cell(row=merged_range.min_row,
                                          column=merged_range.min_col).value
                return return_val

        return cell.value
