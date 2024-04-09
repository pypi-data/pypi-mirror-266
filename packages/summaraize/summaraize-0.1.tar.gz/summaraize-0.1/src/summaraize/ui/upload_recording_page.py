from typing import TYPE_CHECKING
import queue
import tkinter as tk
from tkinter import filedialog
import ttkbootstrap as ttk
from ttkbootstrap.dialogs.dialogs import Messagebox, MessageDialog
from .spinner import Spinner
from .config import whisper_languages, select_video_label_text
if TYPE_CHECKING:
    from .ui import App


class UploadRecordingPage(ttk.Frame):
    """Ask user to select video recording and language"""
    def __init__(self, master: 'App'):
        super().__init__(master)
        ttk.Label(self, text="Select Recording", font=("Helvetica", 24)).pack(pady=10)
        self.selector_btn = ttk.Button(self, text="Select File", command=self.select_file)
        self.selector_btn.pack(pady=10)
        self.language_var = tk.StringVar()
        ttk.Label(self, text="Recording Language").pack(padx=10, pady=5)
        ls = ttk.OptionMenu(self, self.language_var, "English", *whisper_languages.keys())
        ls.pack(padx=10, pady=5)
        ttk.Label(self, text=select_video_label_text).pack(pady=10, padx=5)
        self.spinner = Spinner(self, text="", font=("Helvetica", 14))
        self.spinner.pack(pady=5, padx=5)
        self.progress = ttk.Progressbar(self, orient="horizontal", length=400, mode="determinate")
        self.progress.pack(pady=20)
        self.progress['value'] = 0
        self.master: 'App' = master
        self.file_path = ""

    def select_file(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            md = MessageDialog(
                f"Extracting transcript of file:\n{file_path}\nLanguage: {self.language_var.get()}",
                title="Confirm Selection",
                buttons=['Confirm:success', 'Cancel:secondary'],
                parent=self,
            )
            md.show()
            if md.result == "Confirm":
                self.file_confirmed(file_path)

    def file_confirmed(self, file_path: str):
        self.file_path = file_path
        self.selector_btn["state"] = "disabled"
        self.progress['value'] = 5
        self.master.params.language = self.language_var.get()
        # signature: convert(file_path, language=sel_lan, chunk=secs | default])
        task_item = ("convert", (self.file_path,),
                     {"language": whisper_languages[self.master.params.language]})
        self.master.task_queue.put(task_item)
        self.after(200, lambda: self.process_queue(0))

    def process_queue(self, counter):
        # pylint: disable=R0801
        self.spinner.spin(counter)
        try:
            result = self.master.result_queue.get_nowait()
        except queue.Empty:
            self.after(200, lambda: self.process_queue(counter + 1))
            return
        if isinstance(result, int):
            self.progress['value'] = result
            self.after(200, lambda: self.process_queue(counter + 1))
        elif isinstance(result, str):
            self.master.params.transcript = result
            self.master.switch_frame("SummarisePage")
        else:
            self.progress['value'] = 0
            self.selector_btn["state"] = "normal"
            self.spinner.config(text="")
            self.file_path = ""
            if isinstance(result, Exception):
                Messagebox.show_error(
                    f"Creating Transcript of {self.file_path} failed.\nError: {result}",
                    "Failed to create transcript", alert=True, width=200)
            else:
                Messagebox.show_error(
                    "Creating Transcript failed.\nError: Internal Server Error",
                    "Failed to create transcript", alert=True, width=200)
