"""
This module defines the main Dotacovatko class containing all the overall app logic for rendering
its window and for managing the invocation of all methods needed for its functionality
"""
import threading
from pathlib import Path
from tkinter import filedialog
from typing import Any

from customtkinter import CTk

from src.Enums import ErrNoEnum
from src.Services import ExcelProcessor
from src.Utils import ErrorHandler, SuccessHandler
from src.Utils.app_error import AppError
from Widgets import ButtonBase, FrameBase, LabelBase, ProgressBarBase


class Dotacovatko(CTk):
    """
    class containing the main app
    """
    def __init__(self):
        super().__init__()
        self._excel_processor: ExcelProcessor = ExcelProcessor()

        self.title("Dotační můstek")

        self._frame: FrameBase = FrameBase(master=self)

        self._frame.pack(fill="both", expand=True)

        self._progress_bar: ProgressBarBase = ProgressBarBase(master=self._frame,
                                             mode="indeterminate")

        self._widgets: list[Any] = []

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
                                          text=f"Složka pro uložení výsledného souboru: "
                                               f"{Path.cwd().name!s}",
                                          text_color="green"))
        self._widgets.append(self._output_widgets)

        self._start_widgets = (ButtonBase(master=self._frame,
                                          command=self._threaded_start,
                                          text="Start"),
                               LabelBase(master=self._frame,
                                         text=""))
        self._widgets.append(self._start_widgets)

        self._arrange_widgets()

    def _arrange_widgets(self) -> None:
        """
        arranges widgets into a grid layout within the app's frame, uses the private variables
        self._widgets and self._frame
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
        file_path = Path(filedialog.askopenfilename(filetypes=file_types,
                                                    initialdir=Path.cwd()))

        if file_path:
            self._excel_processor.set_input(file_path)
            self._input_widgets[1].configure(text=f"Soubor {file_path.name!s} úspěšně načten.",
                                             text_color="green")
        else:
            self._input_widgets[1].configure(
                text="Chyba při otevírání Excel souboru na vstup.",
                text_color="red")

    def _choose_output_folder(self) -> None:
        """
        Lets the user choose an output folder for the processed Excel file, sets it up in the
        ExcelProcessor
        :return: None
        """
        directory_path = Path(filedialog.askdirectory(initialdir=Path.cwd()))

        if directory_path:
            self._excel_processor.set_output_directory(directory_path)
            self._output_widgets[1].configure(text=f"Složka pro uložení výsledného souboru: "
                                                    f"{directory_path.name!s}",
                                              text_color="green")
        else:
            self._output_widgets[1].configure(text="Chyba při načítání složky pro výstup.",
                                              text_color="red")

    def _threaded_start(self) -> None:
        """
        Starts the background processes inside a thread to ensure the UI stays responsive
        :return: None
        """
        self._start_widgets[1].configure(text="")

        self._progress_bar.grid(row=self._start_widgets[1].grid_info()["row"],
                                column=self._start_widgets[1].grid_info()["column"])
        self._progress_bar.start()

        background_thread = threading.Thread(target=self._bg_processing, daemon=True)
        background_thread.start()

    def _bg_processing(self) -> None:
        """
        Method used to dictate how the background processing of data is run and how the UI responds
        :return: None
        """
        try:
            if not self._excel_processor.load_template():
                self.after(0, self.__handle_failure,
                           ErrNoEnum.ERR_FAILED_TO_DOWNLOAD, "Chyba během stahování šablony.")
                return

            if not self._excel_processor.load_data():
                self.after(0, self.__handle_failure,
                           ErrNoEnum.ERR_OPENING_EXCEL, "Chyba během načítání dat.")
                return

            if not self._excel_processor.process_input_data():
                self.after(0, self.__handle_failure,
                           ErrNoEnum.ERR_WORKING_WITH_EXCEL, "Chyba během zpracování dat")
                return

            self.after(0, self.__handle_success)

        except AppError as e:
            self.after(0, self.__handle_failure, e.error_code, e.error_message)

        except Exception as e:
            self.after(0, self.__handle_failure,
                       ErrNoEnum.INTERNAL_ERROR, f"Neočekávaná chyba {e}")

    def __handle_success(self) -> None:
        """
        Method used to have the UI react to a successful
        :return:
        """
        self._progress_bar.stop()
        self._progress_bar.grid_forget()
        self._start_widgets[1].configure(text="Data úspěšně zpracována", text_color="green")
        SuccessHandler()

    def __handle_failure(self, error_code: ErrNoEnum, error_msg: str) -> None:
        self._progress_bar.stop()
        self._progress_bar.grid_forget()
        ErrorHandler(error_code=error_code, error_message=error_msg)
        self._start_widgets[1].configure(text=error_msg, text_color="red")

if __name__ == "__main__":
    app = Dotacovatko()
    app.mainloop()
