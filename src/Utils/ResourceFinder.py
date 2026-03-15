import sys
import os

class ResourceFinder:
    @staticmethod
    def resource_path(relative_path: str) -> str:
        """
        Get absolute path to resource, works for dev and for PyInstaller.
        :param relative_path: relative path to the resource, IE where it is
        :return: path to the resource during runtime
        """
        try:
            base_path = sys._MEIPASS
        except AttributeError:
            base_path = os.path.abspath("")

        return os.path.join(base_path, relative_path)