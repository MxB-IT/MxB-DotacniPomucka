"""Defines the base class for all buttons in the project."""
from typing import Any

from customtkinter import CTkButton

from src.Enums import ColourEnum


class ButtonBase(CTkButton):
    """Base class for all the buttons in this project."""

    def __init__(self,
                 *args: tuple[Any, ...],
                 fg_color : ColourEnum = ColourEnum.DARK_MXB_RED,
                 **kwargs: Any) -> None:
        """Initialise the button.

        Initialises the button with the given arguments modifying its initial appearance
        :param args: Any positional arguments to be passed to the ButtonBase superclass.
        :param fg_color: colour this should have, defaults to DARK_MXB_RED
        :param kwargs: Any keyword arguments to be passed to the ButtonBase superclass.
        :return: None
        """
        super().__init__(*args,
                         fg_color=fg_color,
                         **kwargs)
