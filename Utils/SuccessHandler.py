from tkinter.constants import BOTH
from customtkinter import CTkToplevel
from Widgets import LabelBase, ButtonBase, FrameBase

class SuccessHandler(CTkToplevel):
    """
    Used to initialize a window indicating a success of the underlying script, carrying a default success message
    """
    def __init__(self):
        super().__init__()
        self.title("Úspěch!")
        self.frame = FrameBase(master=self)
        self.frame.pack(fill=BOTH,
                        expand=True)

        self.widgets = list()

        self.label = LabelBase(master=self.frame,
                               text=f"Excel soubor úspěšně zpracován")
        self.widgets.append(self.label)

        self.button = ButtonBase(master=self.frame,
                                 command=self.destroy,
                                 text="OK")
        self.widgets.append(self.button)

        for widget in self.widgets:
            widget.pack(padx=5,
                        pady=5,
                        fill=BOTH,
                        expand=True)