class SeparatorGetter:
    @staticmethod
    def get_separator(file_path: str) -> str:
        """
        gets the file separator valid for the OS ('/' for unix or '\' for Windows)
        :param file_path: filepath to be analyzed
        :return: str representing the file separator present within the filepath
        """
        if "/" in file_path:
            return "/"
        else:
            return "\\"