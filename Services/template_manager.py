import tempfile
import time
import zipfile
import re
from typing import Tuple

import requests
import os
from openpyxl import load_workbook

from Enums import ErrNoEnum
from Utils.ErrorHandler import ErrorHandler


class TemplateManager:
    """
    This class handles downloading the template for the output Excel sheet, if it has already been downloaded previously,
    it does not download anything, using the already downloaded file
    """
    def __init__(self, template_url: str) -> None:
        self._url = template_url
        self._app_name = 'Dotacovatko'
        self.path = self._get_writable_path()

    def _get_writable_path(self) -> str:
        """
        This method finds the best place to store the template file, it goes APPPDATA -> Documents -> system temp
        :return: filepath which will be written into
        """
        appdata = os.path.join(os.environ.get('LOCALAPPDATA', ''), self._app_name)
        documents = os.path.join(os.path.expanduser('~'), "Documents", self._app_name)
        system_temp = os.path.join(tempfile.gettempdir(), self._app_name)

        for path in [appdata, documents, system_temp]:
            try:
                os.makedirs(path, exist_ok=True)
                test_file = os.path.join(path, 'permsTest')
                with open(test_file, "w") as f:
                    f.write('test')
                os.remove(test_file)

                return os.path.join(path, f"MPSV_Template_{time.strftime('%Y')}.xlsx")
            except (OSError, IOError) as e:
                continue

        raise PermissionError("Aplikace nebyla schopna najít složku, do které by mohla stáhnout a uložit Excel MPSV.")

    def _is_template_ready(self) -> bool:
        """
        Checks whether the template has already been downloaded
        :return: True if it has already been downloaded, False otherwise
        """
        return os.path.exists(self.path)

    def download_template(self) -> bool:
        """
        Downloads the template file from the URL and stores it in the specified filepath
        :return: True if the download succeeds, false otherwise
        """
        if self._is_template_ready():
            self._scrub_template()
            return True

        try:
            response = requests.get(self._url)
            response.raise_for_status()

            with open(self.path, "wb") as file:
                file.write(response.content)

            if not self._scrub_template():
                return False
            return True

        except Exception as e:
            ErrorHandler(error_code= ErrNoEnum.ERR_FAILED_TO_DOWNLOAD,
                         error_message="Chyba při načítání šablony, zkuste to prosím znovu")
            return False

    def _scrub_template(self) -> bool:
        """
        Removes certain metadata from the template that caused an error when opening
        :return: bool indicating success or failure
        """
        temp_file = self.path + ".tmp"

        try:
            with zipfile.ZipFile(self.path, "r") as zin:
                with zipfile.ZipFile(temp_file, "w") as zout:
                    for item in zin.infolist():
                        data = zin.read(item.filename)

                        if item.filename == 'xl/workbook.xml':
                            xml_content = data.decode('utf-8')
                            xml_content = re.sub(r'<definedNames>.*?</definedNames>', '', xml_content, flags=re.DOTALL)
                            data = xml_content.encode('utf-8')

                        zout.writestr(item, data)

            os.replace(temp_file, self.path)
            return True
        except Exception as e:
            if os.path.exists(temp_file):
                os.remove(temp_file)

            ErrorHandler(error_code=ErrNoEnum.ERR_FAILED_TO_DOWNLOAD,
                         error_message="Chyba při načítání šablony, zkuste to prosím znovu")
            return False

    def update_template_cell(self, sheet_name: str, cell_coord: Tuple[int, int], value: str) -> bool:
        """
        Updates a specific cell inside an existing Excel file without deleting everything in it
        :param sheet_name: name of the sheet the cell is in
        :param cell_coord: coordinates of the cell
        :param value: value to write into the cell
        :return:
        """
        wb = load_workbook(self.path)
        ws = wb[sheet_name]

        ws[cell_coord].value = value

        try:
            wb.save(self.path)
        except (OSError, IOError) as e:
            ErrorHandler(error_code=ErrNoEnum.ERR_FAILED_TO_SAVE,
                         error_message="Upravený soubor se nepodařilo uložit, ujistěte se, že jej nemáte nikde otevřený a zkuste to prosím znovu.")
            return False

        wb.close()
        return True