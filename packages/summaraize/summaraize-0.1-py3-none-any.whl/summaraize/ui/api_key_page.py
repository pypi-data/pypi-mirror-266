from typing import TYPE_CHECKING
import ttkbootstrap as ttk
from ttkbootstrap.dialogs.dialogs import Messagebox
from .config import api_key_label_text
if TYPE_CHECKING:
    from .ui import App


class ApiKeyPage(ttk.Frame):
    """Show when OPENAI API KEY not in env or does not work"""
    def __init__(self, master: 'App'):
        super().__init__(master)
        ttk.Label(self, text="Set OpenAI Api Key", font=("Helvetica", 24)).pack(pady=20, padx=20)
        self.api_key_entry = ttk.Entry(self)
        self.api_key_entry.pack()
        ttk.Button(self, text="Set", command=self.save_api_key,
                   width=20, style="TButton").pack(pady=40, padx=10)
        ttk.Label(self, text=api_key_label_text).pack(pady=10, padx=5)
        self.master: 'App' = master

    def save_api_key(self):
        api_key = self.api_key_entry.get()
        if api_key is None or api_key == "":
            return
        try:
            self.master.summarize.set_api_key(api_key)
        # pylint: disable=broad-exception-caught
        except Exception as e:
            Messagebox.show_error(f"Error: {str(e)}",
                                  "Failed to set OpenAI api key",
                                  alert=True, width=200)
            return
        self.master.switch_frame("UploadRecordingPage")
