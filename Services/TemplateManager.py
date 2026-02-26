import tempfile
import time
import requests
import os

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
                os.makedirs(path)
                test_file = os.path.join(path, 'permsTest')
                with open(test_file, "w") as f:
                    f.write('test')
                os.remove(test_file)

                return os.path.join(path, f"MPSV_Template_{time.strftime('%Y')}.xlsx")
            except (OSError, IOError) as e:
                continue

        raise PermissionError("Aplikace nebyla schopna najít složku, do které by mohla stáhnout a uložit Excel MPSV.")

    def is_template_ready(self) -> bool:
        """
        Checks whether the template has already been downloaded
        :return: True if it has already been downloaded, False otherwise
        """
        return os.path.exists(self.path)

    def download_template(self) -> bool:
        """
        Downloads the template file from the URL and stores it in the specified filepath
        :return: True is the download succeeds, false otherwise
        """
        try:
            response = requests.get(self._url)
            response.raise_for_status()

            with open(self.path, "wb") as file:
                file.write(response.content)
            return True

        except Exception as e:
            ErrorHandler(error_code= ErrNoEnum.ERR_FAILED_TO_DOWNLOAD, error_message="Chyba při načítání šablony, zkuste to prosím znovu")
            return False