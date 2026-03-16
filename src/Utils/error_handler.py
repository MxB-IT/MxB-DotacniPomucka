"""
This module defines the ErrorHandler class, meant as a utility class for processing and displaying
error messages to the end user as a pop-up window
"""
from tkinter.constants import BOTH

from customtkinter import CTkToplevel

from src.Widgets import ButtonBase, FrameBase, LabelBase


class ErrorHandler(CTkToplevel):
    """
    Class used as a utility to display error messages to the user inside a pop-up window
    """
    def __init__(self,
                 *args,
                 error_message: str,
                 error_code: int,
                 **kwargs):
        super().__init__(*args,
                         **kwargs)
        self.title("ERROR")
        self.frame = FrameBase(master=self)
        self.frame.pack(fill=BOTH,
                        expand=True)
        self.widgets = list()
        self.error_message = LabelBase(master=self.frame,
                                       text=f"ERROR {error_code}: {error_message}")
        self.widgets.append(self.error_message)

        self.done_button = ButtonBase(master=self.frame,
                                      text="OK",
                                      command=self.destroy)
        self.widgets.append(self.done_button)

        for widget in self.widgets:
            widget.pack(padx=5,
                        pady=5,
                        fill=BOTH,
                        expand=True)
