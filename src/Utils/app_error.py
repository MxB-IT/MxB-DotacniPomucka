"""
This module contains the definition of an error class for carrying errors that the app may raise
during runtime
"""
from src.Enums import ErrNoEnum


class AppError(Exception):
    """
    Base class for all errors raised by the app
    """
    def __init__(self, error_code: ErrNoEnum, error_message: str) -> None:
        self.error_code: ErrNoEnum = error_code
        self.error_message: str = error_message
        super().__init__(f"[{error_code.name}] {error_message}")
