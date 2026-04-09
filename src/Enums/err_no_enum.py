"""
This module defines the enum with error numbers for every kind of error the application could
potentially run into
"""
from enum import IntEnum


class ErrNoEnum(IntEnum):
    """
    IntEnum with all the error codes
    """
    ERR_OPENING_EXCEL = 401
    ERR_SELECTING_OUTPUT = 402
    ERR_FAILED_TO_DOWNLOAD = 403
    ERR_FAILED_TO_SAVE = 404
    ERR_WORKING_WITH_EXCEL = 405
    ERR_EMPLOYEE_MANDATORY_ATTR_NOT_SET = 501
    INTERNAL_ERROR = 999
