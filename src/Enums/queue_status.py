"""Enum containing all queue statuses used in the multiprocessing queues."""

from enum import StrEnum


class QueueStatus(StrEnum):
    """Class containing all queue statuses used in the multiprocessing queues."""

    SUCCESS = "success"
    INTERRUPT = "interrupt"
