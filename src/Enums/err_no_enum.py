"""Defines an enum with all error codes inside it."""
from enum import IntEnum


class ErrNoEnum(IntEnum):
    """IntEnum with all the error codes used within the app."""

    ERR_OPENING_EXCEL = 401
    ERR_SELECTING_OUTPUT = 402
    ERR_FAILED_TO_DOWNLOAD = 403
    ERR_FAILED_TO_SAVE = 404
    ERR_WORKING_WITH_EXCEL = 405
    ERR_EMPLOYEE_MANDATORY_ATTR_NOT_SET = 501
    ERR_EMPLOYEE_MISSING = 502
    ERR_FAILED_TO_FIND_WRITABLE = 301
    ERR_UNKNOWN_QUEUE_MESSAGE = 601
    INTERNAL_ERROR = 999
