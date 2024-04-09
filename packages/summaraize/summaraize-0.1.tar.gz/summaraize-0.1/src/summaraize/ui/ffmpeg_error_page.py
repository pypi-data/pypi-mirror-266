from typing import TYPE_CHECKING
import sys
import ttkbootstrap as ttk
from .config import ffmpeg_missing_text
if TYPE_CHECKING:
    from .ui import App


class FfmpegErrorPage(ttk.Frame):
    """Show when no FFmpeg in system"""
    def __init__(self, master: 'App'):
        super().__init__(master)
        ttk.Label(
            self, text=ffmpeg_missing_text,
            font=("Helvetica", 24)).pack(pady=20, padx=20)
        ttk.Button(self, text="Exit", command=self.exit,
                   width=20, style="TButton").pack(pady=40, padx=10)

    def exit(self):
        sys.exit(1)
