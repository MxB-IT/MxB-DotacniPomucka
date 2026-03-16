"""
This module defines the Tooltip class used to define how tooltips should behave and look within the
GUI of the app
"""
from customtkinter import CTkLabel, CTkToplevel


class Tooltip:
    """
    class used for displaying tooltips to the user upon hovering over certain elements of the app
    """
    def __init__(self,
                 widget,
                 text: str,
                 delay: int = 500):
        """
        initializer for the Tooltip class, sets up all the private properties and binds the
        appropriate actions
        :param widget: widget for which the tooltip will be shown
        :param text: text the tooltip will display
        :param delay: delay after which the tooltip will appear (in ms)
        """
        self._widget = widget
        self._text = text
        self._delay = delay
        self._tooltip_window = None
        self._id = None

        self._widget.bind("<Enter>", self._schedule_tooltip)
        self._widget.bind("<Leave>", self._hide_tooltip)
        self._widget.bind("ButtonPress", self._hide_tooltip)

    def _schedule_tooltip(self) -> None:
        """
        method used for scheduling a tooltip to show itself, called whenever a user mouses over the
        appropriate widget
        :return: None
        """
        self._id = self._widget.after(self._delay, self._show_tooltip)

    def _show_tooltip(self) -> None:
        """
        method used to calculate the size of the tooltip and its position relative to the parent
        widget
        :return: None
        """
        x = self._widget.winfo_rootx() + 20
        y = self._widget.winfo.rooty() + self._widget.winfo_height() + 5

        self._tooltip_window = CTkToplevel(master=self._widget)
        self._tooltip_window.wm_overrideredirect(True)
        self._tooltip_window.geometry(f"+{x}+{y}")
        self._tooltip_window.attributes("-topmost", True)

        label = CTkLabel(
            master=self._tooltip_window,
            text=self._text,
            fg_color="#333333",
            text_color="#FFFFFF",
            corner_radius=6,
            font=("Arial", 12),
            padx=10,
            pady=5
        )

        label.pack()

    def _hide_tooltip(self) -> None:
        """
        method used to hide the tooltip, called after user action or timeout
        :return: None
        """
        if self._id:
            self._widget.after_cancel(self._id)
            self._id = None

        if self._tooltip_window:
            self._tooltip_window.destroy()
            self._tooltip_window = None
