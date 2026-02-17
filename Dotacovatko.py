import os
from tkinter import Widget
from typing import List, Tuple

from customtkinter import CTk, CTkFrame

from Utils.SeparatorGetter import SeparatorGetter
from Widgets import ButtonBase, LabelBase, FrameBase, Tooltip

class Dotacovatko(CTk):
    """
    class containing the main app
    """
    def __init__(self):
        super().__init__()
        self.title("Dotační můstek")

        self._output_directory = os.getcwd()
        self._frame = FrameBase(master=self)

        self._widgets = list()

        self.input_widgets = (ButtonBase(master=self.frame,
                                      command=self.open_input,
                                      text="Načíst vstupní tabulku"),
                           LabelBase(master=self._frame,
                                     text="Nebyla načtena žádná vstupní tabulka",
                                     text_color="red"))
        self._widgets.append(self.input_widgets)

        self.output_widgets = (ButtonBase(master=self.frame,
                                          command=self.choose_output_folder,
                                          text="Zvolit složku pro uložení výsledného souboru"),
                               LabelBase(master=self._frame,
                                         text=f"Složka pro uložení výsledného souboru: {str(self._output_directory.split(SeparatorGetter.get_separator(self._output_directory))[-1])}",
                                         text_color="green"))
        self._widgets.append(self.output_widgets)

    def arrange_widgets(self) -> None:
        """
        arranges widgets into a grid layout within the app's frame, uses the private variables self._widgets and self._frame
        :return: None
        """
        for i, row in enumerate(self._widgets):
            for j, widget in enumerate(row):
                widget.grid(row=i,
                            column=j,
                            padx=10,
                            pady=10)
                self._frame.columnconfigure(index=j,
                                            weight=1)
            self._frame.rowconfigure(index=i,
                                     weight=1)

if __name__ == '__main__':
    app = Dotacovatko()
    app.mainloop()