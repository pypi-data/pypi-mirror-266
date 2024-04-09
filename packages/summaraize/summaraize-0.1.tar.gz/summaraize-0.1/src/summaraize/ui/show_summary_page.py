from typing import TYPE_CHECKING
import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.dialogs.dialogs import Messagebox
from .markdown import SimpleMarkdownText
if TYPE_CHECKING:
    from .ui import App


class ShowSummaryPage(ttk.Frame):
    """Show summary from GPT"""
    def __init__(self, master: 'App'):
        super().__init__(master)
        self.text = SimpleMarkdownText(master,
                                       width=45,
                                       height=22,
                                       font=tk.font.Font(family="Helvetica", size=12))
        self.text.pack(fill="both", expand=True)
        self.text.insert_markdown(master.params.result)
        buttons = ttk.Frame(self)
        buttons.pack(pady=10)
        ttk.Button(buttons, text="New Summary",
                   command=self.back,
                   style='Outline.TButton').pack(side="left", padx=5)
        self.clipboard_btn = ttk.Button(buttons,
                                        text="Copy to Clipboard",
                                        command=self.copy_to_clipboard,
                                        style="TButton")
        self.clipboard_btn.pack(side="left", padx=5)
        ttk.Button(buttons, text="Save to File",
                   command=self.save_file,
                   style="TButton").pack(padx=5)
        self.copied_label = tk.Label(self, text="")
        self.copied_label.pack(pady=10)
        self.master: 'App' = master

    def save_file(self):
        filename = tk.filedialog.asksaveasfilename(defaultextension="md")
        if filename is None:
            return
        with open(filename, 'w', encoding='utf8') as f:
            f.write(self.master.params.result)
        Messagebox.ok(f"File {filename} Saved Successfully", width=200)
        self.text.pack_forget()
        self.master.switch_frame("SummarisePage")

    def copy_to_clipboard(self):
        self.master.clipboard_clear()
        self.master.clipboard_append(self.master.params.result)
        self.copied_label.config(text="Text copied to clipboard!")
        self.after(2000, lambda: self.copied_label.config(text=""))

    def back(self):
        self.text.pack_forget()
        self.master.switch_frame("SummarisePage")
