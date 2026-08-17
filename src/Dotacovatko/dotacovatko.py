"""Defines the main app class, which services the GUI and invokes the underlying scripts."""
import multiprocessing
from pathlib import Path
from queue import Empty
from tkinter import filedialog
from typing import Any

from customtkinter import CTk  # type: ignore[import-untyped]

from Enums import ErrNoEnum
from Enums.queue_status import QueueMessages
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

        self.title("Dotační můstek")

        self.__frame: FrameBase = FrameBase(master=self)

        self.__frame.pack(fill="both", expand=True)

        self.__progress_bar: ProgressBarBase = ProgressBarBase(master=self.__frame,
                                                               mode="indeterminate")

        self.__widgets: list[Any] = []

        self.__input_widgets = (ButtonBase(master=self.__frame,
                                           command=self._open_input,
                                           text="Načíst vstupní tabulku"),
                                LabelBase(master=self.__frame,
                                         text="Nebyla načtena žádná vstupní tabulka",
                                         text_color="red"))
        self.__widgets.append(self.__input_widgets)

        self._output_widgets = (ButtonBase(master=self.__frame,
                                           command=self._choose_output_folder,
                                           text="Zvolit složku pro uložení výsledného souboru"),
                                LabelBase(master=self.__frame,
                                          text=f"Složka pro uložení výsledného souboru: "
                                               f"{Path.cwd().name!s}",
                                          text_color="green"))
        self.__widgets.append(self._output_widgets)

        self.__start_widgets = (ButtonBase(master=self.__frame,
                                           command=self._threaded_start,
                                           text="Start"),
                                LabelBase(master=self.__frame,
                                         text=""))
        self.__widgets.append(self.__start_widgets)

        self.__arrange_widgets()

        self.__outbound_queue: multiprocessing.Queue[AppError | float | QueueMessages] = multiprocessing.Queue()
        self.__inbound_queue: multiprocessing.Queue[QueueMessages] = multiprocessing.Queue()
        self.__bg_process: multiprocessing.Process
        self.__input_file: Path
        self.__output_dir: Path

        self.protocol("WM_DELETE_WINDOW", self.__stop_processing)

    def __arrange_widgets(self) -> None:
        """Arrange widgets into an array.

        Arranges widgets into a grid layout within the app's frame, uses the private variables
        self._widgets and self._frame.
        :return: None.
        """
        for i, row in enumerate(self.__widgets):
            for j, widget in enumerate(row):
                widget.grid(row=i,
                            column=j,
                            padx=10,
                            pady=10)
                self.__frame.columnconfigure(index=j,
                                             weight=1)
            self.__frame.rowconfigure(index=i,
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
            self.__input_file = file_path
            self.__input_widgets[1].configure(text=f"Soubor {file_path.name!s} úspěšně načten.",
                                              text_color="green")
        else:
            self.__input_widgets[1].configure(
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
            self.__output_dir = directory_path
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
        self.__start_widgets[1].configure(text="")

        self.__progress_bar.grid(row=self.__start_widgets[1].grid_info()["row"],
                                 column=self.__start_widgets[1].grid_info()["column"])
        self.__progress_bar.start()

        self.__bg_process = multiprocessing.Process(
            target=Dotacovatko.run_background_processing,
            args=(
                self.__outbound_queue,
                self.__inbound_queue,
                self.__input_file,
                self.__output_dir,
            ),
            daemon=True,
        )

        self.__bg_process.start()

        self._check_queue()

    def _check_queue(self) -> None:
        """Check queue for multiprocessing messages.

        Method used to poll the multiprocessing queue for messages from the processing
        multiprocessing instance.
        :return: None.
        """
        try:
            message = self.__outbound_queue.get_nowait()

            match message.__class__.__name__:
                case QueueMessages.__name__:
                    if message == QueueMessages.SUCCESS:
                        self.__handle_success()

                case AppError.__name__:
                    self.__handle_failure(message)

                case _:
                    self.__handle_failure(
                        error=AppError(
                            error_code=ErrNoEnum.ERR_UNKNOWN_QUEUE_MESSAGE,
                            error_message="Vnitřní chyba programu, zkuste to prosím znovu.",
                        ),
                    )

        except Empty:
            self.after(100, self._check_queue)

    def __handle_success(self) -> None:
        """Handle a success report from underlying scripts.

        Method used to have the UI react to a successful.
        :return: None.
        """
        self.__progress_bar.stop()
        self.__progress_bar.grid_forget()
        self.__start_widgets[1].configure(text="Data úspěšně zpracována", text_color="green")
        SuccessHandler()

    def __handle_failure(self,
                         error: AppError) -> None:
        self.__progress_bar.stop()
        self.__progress_bar.grid_forget()
        ErrorHandler(error_code=error.error_code, error_message=error.error_message)
        self.__start_widgets[1].configure(text=error.error_message, text_color="red")

    @staticmethod
    def run_background_processing(inbound_queue: multiprocessing.Queue[AppError | float | QueueMessages],
                                  outbound_queue: multiprocessing.Queue[QueueMessages],
                                  input_path: Path,
                                  output_dir: Path) -> None:
        """Run the background processing process.

        Manages multiprocessing invocation of the ExcelProcessor class and puts it to work
        analysing the Excel data.
        :param inbound_queue: Multiprocessing queue for receiving messages from the GUI.
        :param outbound_queue: Multiprocessing queue for sending messages to the GUI.
        :param input_path: Path to the input file to be passed to the ExcelProcessor.
        :param output_dir: Output directory to be passed to the ExcelProcessor.
        :return: None.
        """
        try:
            processor = ExcelProcessor(
                inbound_queue=outbound_queue,
                outbound_queue=inbound_queue,
                input_path=input_path,
                output_directory=output_dir,
            )

            processor.run()

            outbound_queue.put(QueueMessages.SUCCESS)

        except AppError as e:
            inbound_queue.put(e)

        except Exception:
            inbound_queue.put(
                AppError(
                    error_code=ErrNoEnum.INTERNAL_ERROR,
                    error_message="Neznámá chyba, zkontrolujte vstupní soubor a zkuste to prosím znovu.",
                ),
            )

    def _send_msg(self,
                  message: QueueMessages) -> None:
        """Send a message to the service running in the background."""
        self.__outbound_queue.put(message)

    def __stop_processing(self) -> None:
        """Interrupt the background processes and end them when the app is closed.

        :return: None.
        """
        self._send_msg(QueueMessages.INTERRUPT)

        self.destroy()
