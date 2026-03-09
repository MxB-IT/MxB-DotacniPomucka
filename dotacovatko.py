from Services import ExcelProcessor
from Utils.SeparatorGetter import SeparatorGetter
from Widgets import ButtonBase, LabelBase, FrameBase, ProgressBarBase

import os
import threading
from tkinter import filedialog
from customtkinter import CTk, CTkProgressBar


class Dotacovatko(CTk):
    """
    class containing the main app
    """
    def __init__(self):
        super().__init__()
        self._excel_processor = ExcelProcessor()

        self.title("Dotační můstek")

        self._frame = FrameBase(master=self)

        self._frame.pack(fill="both", expand=True)

        self._progress_bar = ProgressBarBase(master=self._frame,
                                             mode="indeterminate")

        self._widgets = list()

        self._input_widgets = (ButtonBase(master=self._frame,
                                          command=self._open_input,
                                          text="Načíst vstupní tabulku"),
                               LabelBase(master=self._frame,
                                         text="Nebyla načtena žádná vstupní tabulka",
                                         text_color="red"))
        self._widgets.append(self._input_widgets)

        self._output_widgets = (ButtonBase(master=self._frame,
                                           command=self._choose_output_folder,
                                           text="Zvolit složku pro uložení výsledného souboru"),
                                LabelBase(master=self._frame,
                                          text=f"Složka pro uložení výsledného souboru: {str(os.getcwd().split(SeparatorGetter.get_separator(os.getcwd()))[-1])}",
                                          text_color="green"))
        self._widgets.append(self._output_widgets)

        self._start_widgets = (ButtonBase(master=self._frame,
                                          command=self._threaded_start,
                                          text='Start'),
                               LabelBase(master=self._frame,
                                         text=''))
        self._widgets.append(self._start_widgets)

        self._arrange_widgets()

    def _arrange_widgets(self) -> None:
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

    def _open_input(self) -> None:
        """
        lets the user choose an Excel file to open and passes it to the ExcelProcessor
        :return: None
        """
        file_types = [("Excel soubor", "*.xlsx *.xls")]
        file_path = filedialog.askopenfilename(filetypes=file_types,
                                               initialdir=os.getcwd())

        if file_path:
            if self._excel_processor.set_input(file_path):
                self._input_widgets[1].configure(text=f"Soubor {str(file_path.split(SeparatorGetter.get_separator(file_path))[-1])} úspěšně načten.",
                                                 text_color="green")
            else:
                self._input_widgets[1].configure(
                    text=f"Chyba při otevírání Excel souboru na vstup.",
                    text_color="red")

    def _choose_output_folder(self) -> None:
        """
        Lets the user choose an output folder for the processed Excel file, sets it up in the ExcelProcessor
        :return: None
        """
        directory_path = filedialog.askdirectory(initialdir=os.getcwd())

        if directory_path:
            if self._excel_processor.set_output_directory(directory_path):
                self._output_widgets[1].configure(text=f"Složka pro uložení výsledného souboru: {str(directory_path.split(SeparatorGetter.get_separator(directory_path))[-1])}",
                                                  text_color="green")
            else:
                self._output_widgets[1].configure(text=f"Chyba při načítání složky pro výstup.",
                                                  text_color="red")

    def _threaded_start(self) -> None:
        self._start_widgets[1].configure(text="")
        self.update_idletasks(),
        self._progress_bar.grid(row=self._start_widgets[1].grid_info()['row'],
                                column=self._start_widgets[1].grid_info()['column'])

        progressbar_thread = threading.Thread(target=CTkProgressBar.start,
                                              args=(self._progress_bar,))
        progressbar_thread.start()

        background_thread = threading.Thread(target=self._bg_processing, daemon=True)
        background_thread.start()

    def _bg_processing(self) -> None:
        download = self._excel_processor.load_template()
        if not download:
            self._progress_bar.stop()
            self._progress_bar.grid_forget()

            self._start_widgets[1].configure(text="Chyba během stahování šablony MPSV.",
                                             text_color="red")
            return

if __name__ == '__main__':
    app = Dotacovatko()
    app.mainloop()