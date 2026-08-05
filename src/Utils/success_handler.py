"""Defines the class used to service the GUI pertaining to showing a success of teh app."""
from tkinter.constants import BOTH
from typing import Any

from customtkinter import CTkToplevel

from Widgets import ButtonBase, FrameBase, LabelBase


class SuccessHandler(CTkToplevel):
    """Used to initialize a window indicating a success of the app."""

    def __init__(self) -> None:
        """Initialise the SuccessHandler.

        Initialises the SuccessHandler, creating a window with a default success message.
        :return: None.
        """
        super().__init__()
        self.title("Úspěch!")
        self.frame: FrameBase = FrameBase(master=self)
        self.frame.pack(fill=BOTH,
                        expand=True)

        self.widgets: list[Any] = []

        self.label: LabelBase = LabelBase(master=self.frame,
                               text="Excel soubor úspěšně zpracován")
        self.widgets.append(self.label)

        self.button: ButtonBase = ButtonBase(master=self.frame,
                                 command=self.destroy,
                                 text="OK")
        self.widgets.append(self.button)

        for widget in self.widgets:
            widget.pack(padx=5,
                        pady=5,
                        fill=BOTH,
                        expand=True)
