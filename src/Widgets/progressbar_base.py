"""
This module defines the ProgressBarBase class that is used to determine the basic characteristics
of every single ctkProgressBar used within the app GUI
"""
from customtkinter import CTkProgressBar

from src.Enums import ColorEnum


class ProgressBarBase(CTkProgressBar):
    """
    Class containing basic definitions for all progress bars present in the app, mainly
    automatically sets the colors
    for the underlying CTkProgressBar class.
    """
    def __init__(self,
                 *args,
                 fg_color=ColorEnum.MXB_RED,
                 progress_color="white",
                 **kwargs):
        super().__init__(*args,
                         fg_color=fg_color,
                         progress_color=progress_color,
                         **kwargs)
