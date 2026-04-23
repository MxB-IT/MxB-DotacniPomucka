"""Defines the error class used for all app errors."""

from src.Enums import ErrNoEnum


class AppError(Exception):
    """Base class for all errors raised by the app."""

    def __init__(self, error_code: ErrNoEnum, error_message: str) -> None:
        """Initialise the error object.

        Initialises the error object with the given error code and message.
        :param error_code: The error code of the error being raised.
        :param error_message: The message describing the raised error.
        :return: None.
        """
        self.error_code: ErrNoEnum = error_code
        self.error_message: str = error_message
        super().__init__(f"[{error_code.name}] {error_message}")
