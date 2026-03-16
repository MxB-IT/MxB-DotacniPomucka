"""
This module defines the ResourceFinder class, it is never meant to be instantiated and contains a
single method used to locate tkinter resources like images,fonts and such during runtime and
development
"""
import sys
from pathlib import Path


class ResourceFinder:
    """
    The ReourceFinder class is never meant to be instantiated and contains only one static method
    meant to be used to locate where certain tkinter resources (images, fonts, etc.) are located
    during runtime and development
    """
    @staticmethod
    def resource_path(relative_path: Path) -> Path:
        """
        Get absolute path to resource, works for dev and for PyInstaller.
        :param relative_path: relative path to the resource, IE where it is
        :return: path to the resource during runtime
        """
        try:
            base_path = Path(sys._MEIPASS)
        except AttributeError:
            base_path = Path.cwd()

        return base_path / relative_path
