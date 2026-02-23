import requests
import os

from Enums import ErrNoEnum
from Utils.ErrorHandler import ErrorHandler


class TemplateManager:
    """
    This class handles downloading the template for the output Excel sheet, if it has already been downloaded previously,
    it does not download anything, using the already downloaded file
    """
    def __init__(self, template_url, target_path):
        self.url = template_url
        self.path = target_path

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
            response = requests.get(self.url)
            response.raise_for_status()

            with open(self.path, "wb") as file:
                file.write(response.content)
            return True

        except Exception as e:
            ErrorHandler(error_code= ErrNoEnum.ERR_FAILED_TO_DOWNLOAD, error_message="Chyba při načítání šablony, zkuste to prosím znovu")
            return False