"""
This module defines the FrameBase that defines the basic characteristics of every single ctkFrame
that will be used within the app GUI
"""
from tkinter import Canvas

from customtkinter import CTkFrame, CTkToplevel

from src.Enums import ColorEnum


class FrameBase(CTkFrame):
    """
    class used for all the frames an app will need, inherits from CTkFrame
    """
    def __init__(self,
                 *args,
                 master: CTkFrame | Canvas | CTkToplevel,
                 fg_color: str | ColorEnum = "white",
                 border_color: str | ColorEnum = ColorEnum.MXB_RED,
                 border_width: int = 2,
                 **kwargs):
        """
        initialization method used whenever a new Frame needs to be intialized, passes all
        arguments to the super initializer
        :param args: any non-keyword arguments
        :param master: master of the Frame
        :param fg_color: color of the Frame
        :param border_color: color of the Frame's border
        :param border_width: width of the Frame's border
        :param kwargs: any keyword arguments
        """
        super().__init__(*args,
                         master=master,
                         fg_color=fg_color,
                         border_color=border_color,
                         border_width=border_width,
                         **kwargs)
