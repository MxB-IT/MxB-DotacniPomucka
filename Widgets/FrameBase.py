from tkinter import Canvas
from typing import Union
from customtkinter import CTkFrame
from Widgets.Enums.ColorEnum import ColorEnum

class FrameBase(CTkFrame):
    """
    class used for all the frames an app will need, inherits from CTkFrame
    """
    def __init__(self,
                 *args,
                 master: Union[CTkFrame, Canvas],
                 fg_color: Union[str, ColorEnum] = 'white',
                 border_color: Union[str, ColorEnum] = ColorEnum.MXB_RED,
                 border_width: int = 2,
                 **kwargs):
        """
        initialization method used whenever a new Frame needs to be intialized, passes all arguments to the super initializer
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