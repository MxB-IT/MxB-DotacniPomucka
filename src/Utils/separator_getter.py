"""
This module defines the SeparatorGetter class that is never meant to be instantiated and contains a
single static method used to determine whether the user is working on a UNIX or DOS based system
and determines the directory separator for the given system (either a / or a \\) I'm told Python
does this on its own, however I do not trust Python enough so I rather do it myself
"""
class SeparatorGetter:
    """
    The SeparatorGetter class is never meant to be instantiated and as such contains only a single
    static method for getting the separator for the system the program is currently running on
    """
    @staticmethod
    def get_separator(file_path: str) -> str:
        """
        gets the file separator valid for the OS ('/' for unix or '\' for Windows)
        :param file_path: filepath to be analyzed
        :return: str representing the file separator present within the filepath
        """
        if "/" in file_path:
            return "/"
        return "\\"
