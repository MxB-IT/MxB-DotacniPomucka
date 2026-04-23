"""Defines the base class for all the labels within the project."""
from tkinter import Canvas
from typing import Any

from customtkinter import CTkFrame, CTkLabel

from src.Enums import ColourEnum


class LabelBase(CTkLabel):
    """Base class for all labels within the project."""

    def __init__(self,
                 *args: tuple[Any, ...],
                 master: CTkFrame | Canvas,
                 text_color: str | ColourEnum = ColourEnum.MXB_RED,
                 **kwargs: Any) -> None:
        """Initialise the Label.

        Initialises the label with the passed arguments.
        :param args: Positional arguments for the parent CTkLabel class.
        :param master: Master widget.
        :param text_color: Colour for the text held by the label.
        :param kwargs: Keyword arguments for the parent CTkLabel class.
        :return: None
        """
        super().__init__(*args,
                         master=master,
                         text_color=text_color,
                         **kwargs)
