"""Defines a main function used as the entrypoint for the app."""
import multiprocessing

from dotacovatko import Dotacovatko


def main() -> None:
    """Entrypoint for the app."""
    app = Dotacovatko()
    app.mainloop()

if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()
