"""Defines the main app class, which services the GUI and invokes the underlying scripts."""
import multiprocessing
from pathlib import Path
from queue import Empty
from tkinter import filedialog
from typing import Any

from customtkinter import CTk

from Enums import ErrNoEnum
from Services import ExcelProcessor
from Utils import ErrorHandler, SuccessHandler
from Utils.app_error import AppError
from Widgets import ButtonBase, FrameBase, LabelBase, ProgressBarBase


class Dotacovatko(CTk):
    """Contains the main app, GUI servicing and underlying script invocation."""

    def __init__(self) -> None:
        """Initialise the main app.

        Initialises the GUI, all its widgets and prepares the beckground script classes
        (ExcelProcessor and TemplateManager).
        :return: None.
        """
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

        self._queue: multiprocessing.Queue = multiprocessing.Queue()
        self._bg_process: multiprocessing.Process | None = None

    def _arrange_widgets(self) -> None:
        """Arrange widgets into an array.

        Arranges widgets into a grid layout within the app's frame, uses the private variables
        self._widgets and self._frame.
        :return: None.
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
        """Prompt the user to choose an input Excel file.

        Lets the user choose an Excel file to open and passes it to the ExcelProcessor.
        :return: None.
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
        """Prompt the user to choose a folder to which output should be saved.

        Lets the user choose an output folder for the processed Excel file, sets it up in the
        ExcelProcessor.
        :return: None.
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
        """Start the input processing in a background process.

        Starts the background processes inside a thread to ensure the UI stays responsive.
        :return: None.
        """
        self._start_widgets[1].configure(text="")

        self._progress_bar.grid(row=self._start_widgets[1].grid_info()["row"],
                                column=self._start_widgets[1].grid_info()["column"])
        self._progress_bar.start()

        input_path: Path | None = self._excel_processor.file_path
        output_dir: Path | None = self._excel_processor.output_directory

        self._bg_process = multiprocessing.Process(
            target=Dotacovatko.run_background_processing,
            args=(self._queue, input_path, output_dir),
            daemon=True,
        )

        self._bg_process.start()

        self._check_queue()

    def _check_queue(self) -> None:
        """Check queue for multiprocessing messages.

        Method used to poll the multiprocessing queue for messages from the processing
        multiprocessing instance.
        :return: None.
        """
        try:
            status, message = self._queue.get_nowait()

            if status == "success":
                self.__handle_success()
            else:
                self.__handle_failure(ErrNoEnum.INTERNAL_ERROR, message)
        except Empty:
            self.after(100, self._check_queue)

    def __handle_success(self) -> None:
        """Handle a success report from underlying scripts.

        Method used to have the UI react to a successful.
        :return: None.
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

    @staticmethod
    def run_background_processing(queue: multiprocessing.Queue,
                                  input_path: Path,
                                  output_dir: Path) -> None:
        """Run the background processing process.

        Manages multiprocessing invocation of the ExcelProcessor class and puts it to work
        analysing the Excel data.
        :param queue: Multiprocessing queue for communicating with the GUI.
        :param input_path: Path to the input file to be passed to the ExcelProcessor.
        :param output_dir: Output directory to be passed to the ExcelProcessor.
        :return: None.
        """
        try:
            processor = ExcelProcessor()
            processor.set_input(input_path)
            processor.set_output_directory(output_dir)

            processor.load_template()

            processor.load_data()

            if not processor.process_input_data():
                queue.put(("error", "Chyba během zpracování dat."))
                return

            queue.put(("success", "done"))

        except AppError as e:
            print("AppError", e)
            queue.put(("error", (e.error_code, e.error_message)))

        #except Exception as e:
        #    print("exception", e)
        #    queue.put(("error", str(e)))

if __name__ == "__main__":
    multiprocessing.freeze_support()
    app = Dotacovatko()
    app.mainloop()
