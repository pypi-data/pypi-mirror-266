import tkinter as tk

class Spinner(tk.Label):
    """
    Show action on-going to user
    """
    # pylint: disable=dangerous-default-value
    def __init__(self, master, cnf={}, **kw):
        # pylint: disable=too-many-function-args
        tk.Label.__init__(self, master, cnf, **kw)
        self._spinner = ['|', '/', '-', '\\']
        self._len_spinner = len(self._spinner)

    def spin(self, counter: int) -> None:
        self.config(
            text=f"Processing {self._spinner[counter % self._len_spinner]}")
