"""Defines a class used to find the resources needed to run the application."""
import sys
from pathlib import Path


class ResourceFinder:
    """Contains a method used to check whether resources are in cwd or tempfolder."""

    @staticmethod
    def resource_path(relative_path: Path) -> Path:
        """Get path to a requested resource.

        Get absolute path to resource, works for dev and for PyInstaller.
        :param relative_path: Relative path to the resource, IE where it is.
        :return: Path to the resource during runtime.
        """
        try:
            base_path = Path(sys._MEIPASS)
        except AttributeError:
            base_path = Path.cwd()

        return base_path / relative_path
