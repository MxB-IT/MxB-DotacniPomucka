from tkinter import Canvas
from typing import Union
from customtkinter import CTkLabel, CTkFrame

from Enums import ColorEnum


class LabelBase(CTkLabel):
    """
    class used for all label widgets in the app
    """
    def __init__(self,
                 *args,
                 master: Union[CTkFrame, Canvas],
                 text_color: Union[str, ColorEnum] = ColorEnum.MXB_RED,
                 **kwargs):
        """
        initializer method used for initialization of the label widgets, calls the super initializer with passed args
        :param args: non-keyword arguments
        :param master: master of the label widgets, either a CTkFrame or a Canvas
        :param text_color: color of the label text, either a string or a ColorEnum value
        :param kwargs: keyword arguments
        """
        super().__init__(*args,
                         master=master,
                         text_color=text_color,
                         **kwargs)