"""Defines the class used to initialise and service a GUI window for displaying error messages."""
from tkinter.constants import BOTH
from typing import Any

from customtkinter import CTkToplevel

from Widgets import ButtonBase, FrameBase, LabelBase


class ErrorHandler(CTkToplevel):
    """Used as a utility to display error messages to the user inside a pop-up window."""

    def __init__(self,
                 *args: tuple[Any, ...],
                 error_message: str,
                 error_code: int,
                 **kwargs: Any) -> None:
        """Initialise the error handler.

        Initialises the error handler based on the passed arguments.
        :param args: Any positional arguments to be passed to the ErrorHandler superclass.
        :param error_message: Error message to be displayed in the pop-up window.
        :param error_code: Error code to be displayed in the pop-up window.
        :param kwargs: Any keyword arguments to be passed to the ErrorHandler superclass.
        """
        super().__init__(*args,
                         **kwargs)
        self.title("ERROR")
        self.frame: FrameBase = FrameBase(master=self)
        self.frame.pack(fill=BOTH,
                        expand=True)
        self.widgets: list[Any] = []
        self.error_message: LabelBase = LabelBase(master=self.frame,
                                       text=f"ERROR {error_code}: {error_message}")
        self.widgets.append(self.error_message)

        self.done_button: ButtonBase = ButtonBase(master=self.frame,
                                      text="OK",
                                      command=self.destroy)
        self.widgets.append(self.done_button)

        for widget in self.widgets:
            widget.pack(padx=5,
                        pady=5,
                        fill=BOTH,
                        expand=True)
