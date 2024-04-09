import queue
from typing import TYPE_CHECKING
import tkinter.scrolledtext as tkscrolled
import ttkbootstrap as ttk
from ttkbootstrap.dialogs.dialogs import Messagebox
from .spinner import Spinner
from .config import prompt_template_text
if TYPE_CHECKING:
    from .ui import App

class SummarisePage(ttk.Frame):
    """Ask user to input prompt for GPT"""
    def __init__(self, master: 'App'):
        super().__init__(master)
        ttk.Label(
            self,
            text="Write a prompt to instruct GPT-4 to summarize the transcript",
            font=("Helvetica", 24)).pack(pady=10)
        self.prompt_entry = tkscrolled.ScrolledText(
            self, width=40, height=20, wrap="word")
        self.prompt_entry.pack(expand=True, fill="both")

        self.sum_btn = ttk.Button(
            self, text="Summarise",
            command=self.start_summarization,
            style="TButton")
        self.sum_btn.pack(pady=10)
        self.spinner = Spinner(self, text="", font=("Helvetica", 14))
        self.spinner.pack(pady=5, padx=5)
        self.progress = ttk.Progressbar(self, orient="horizontal", length=200, mode="determinate")
        self.progress.pack(pady=10)
        self.prompts = ttk.Text(self, width=40, height=20, wrap="word")
        self.prompts.insert(1.0, master.params.prompt_history + prompt_template_text)
        self.prompts.pack(expand=True, fill="both")
        self.prompts.configure(
            state="disabled",
            inactiveselectbackground=self.prompts.cget("selectbackground"))
        self.master: 'App' = master

    def start_summarization(self):
        user_input = self.prompt_entry.get("1.0", "end-1c")
        if user_input is None or len(user_input) == 0:
            return
        self.sum_btn["state"] = "disabled"
        self.master.params.prompt_history = user_input
        self.progress['value'] = 0
        # signature: summarize(prompt:str, language:str = "English")
        task_item = ("summarize", (user_input,), {"language": self.master.params.language})
        self.master.task_queue.put(task_item)
        self.after(200, lambda: self.process_queue(0))

    def process_queue(self, counter):
        self.spinner.spin(counter)
        try:
            result = self.master.result_queue.get_nowait()
        except queue.Empty:
            self.after(200, lambda: self.process_queue(counter + 1))
            self.progress["value"] = min(90, ((counter // 5) * 100) // 60)
            return
        if isinstance(result, str):
            self.master.params.result = result
            self.master.switch_frame("ShowSummaryPage")
        else:
            self.progress['value'] = 0
            self.sum_btn["state"] = "normal"
            self.spinner.config(text="")
            if isinstance(result, Exception):
                Messagebox.show_error(
                    f"Error: {str(result)}", "Failed to create summary",
                    alert=True, width=200)
            else:
                Messagebox.show_error(
                    f"Internal Server Error: {type(result)} rxd from queue",
                    "Failed to create summary", alert=True, width=200)
            self.master.switch_frame(SummarisePage)
