"""Contains the base class for all service classes, providing the basis for multiprocessing communication."""
import multiprocessing as mp
import threading
from abc import ABCMeta, abstractmethod

from Enums.queue_status import QueueMessages
from Utils.app_error import AppError


class ServiceBase(metaclass=ABCMeta):
    """Serves as a base for all services in the app.

    As such it provides the base methods and infrastructure for multiprocessing communication.
    """

    def __init__(self,
                 inbound_queue: mp.Queue[QueueMessages],
                 outbound_queue: mp.Queue[QueueMessages | AppError | float],
                 ) -> None:
        """Initialise the service base class, giving it a queue.

        :param inbound_queue: Multiprocessing queue used to receive inbound messages from the GUI.
        :param outbound_queue: Multiprocessing queue used to send outbound messages to the GUI.
        """
        self.__inbound_queue: mp.Queue[QueueMessages] = inbound_queue
        self.__outbound_queue: mp.Queue[QueueMessages | AppError | float] = outbound_queue
        self._stop_event: threading.Event = threading.Event()

        __queue_listener: threading.Thread = threading.Thread(
            target=self._queue_listener,
            daemon=True,
        )

    def _queue_listener(self) -> None:
        """Listen to the queue for any incoming messages, passing them over as they arrive.

        :return: None.
        """
        while True:
            msg: QueueMessages = self.__inbound_queue.get()
            if msg == QueueMessages.INTERRUPT:
                self._stop_event.set()
                break

    def _send_msg(self,
                  msg: float | QueueMessages | AppError) -> None:
        """Push the passed message to the outbound queue.

        :param msg: Message to be pushed to the queue.
        :return: None.
        """
        self.__outbound_queue.put(msg)

    @abstractmethod
    def run(self) -> None:
        """Run the underlying service.

        :return: None.
        """
