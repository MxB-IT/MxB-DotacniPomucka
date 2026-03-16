"""
This module defines the ButtonBase used to define the basic characteristics of every single button
that will be used in the app GUI
"""
from customtkinter import CTkButton

from src.Enums import ColorEnum


class ButtonBase(CTkButton):
    """
    class containing the base for all the GUI buttons, inherits from CTkButton
    """
    def __init__(self,
                 *args,
                 fg_color : ColorEnum = ColorEnum.DARK_MXB_RED,
                 **kwargs):
        """
        Button initializer
        :param args: all non keyword arguments
        :param fg_color:
        :param kwargs:
        """
        super().__init__(*args,
                         fg_color=fg_color,
                         **kwargs)
