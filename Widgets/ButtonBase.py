from customtkinter import CTkButton

from Enums.ColorEnum import ColorEnum

"""
class containing the base for all the GUI buttons, inherits from CTkButton
"""
class ButtonBase(CTkButton):
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