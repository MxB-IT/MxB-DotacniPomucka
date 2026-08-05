"""Defines the base class for the progress bar in this project."""
from typing import Any

from customtkinter import CTkProgressBar

from Enums import ColourEnum


class ProgressBarBase(CTkProgressBar):
    """Defines the base behaviour for all progress bars in this project."""

    def __init__(self,
                 *args: tuple[Any, ...],
                 fg_color: ColourEnum=ColourEnum.MXB_RED,
                 progress_color: ColourEnum=ColourEnum.WHITE,
                 **kwargs: Any):
        """Initialise the ProgressBarBase.

        Initialises the ProgressBarBase, modifying its base behaviour based on its arguments.
        :param args: Any positional arguments to be passed to the CTkProgressBar superclass.
        :param fg_color: Colour of the progress bar while in focus.
        :param progress_color: Colour of the progress bar inside the container.
        :param kwargs: Any keyword arguments to be passed to the CTkProgressBar superclass.
        """
        super().__init__(*args,
                         fg_color=fg_color,
                         progress_color=progress_color,
                         **kwargs)
