"""Defines the base class for all Frames within the project."""
from tkinter import Canvas
from typing import Any

from customtkinter import CTkFrame, CTkToplevel

from Enums import ColourEnum


class FrameBase(CTkFrame):
    """Base class for all Frames within the project."""

    def __init__(self,
                 *args: tuple[Any, ...],
                 master: CTkFrame | Canvas | CTkToplevel,
                 fg_color: str | ColourEnum = "white",
                 border_color: str | ColourEnum = ColourEnum.MXB_RED,
                 border_width: int = 2,
                 **kwargs: Any) -> None:
        """Initialise the Frame.

        Initialises the Frame with passed arguments.
        :param args: Positional arguments for the CTkFrame superclass.
        :param master: Master widget.
        :param fg_color: Colour of the Frame.
        :param border_color: Border colour of the Frame.
        :param border_width: Border width of the Frame.
        :param kwargs: Keyword arguments for the CTkFrame superclass.
        :return: None
        """
        super().__init__(*args,
                         master=master,
                         fg_color=fg_color,
                         border_color=border_color,
                         border_width=border_width,
                         **kwargs)
