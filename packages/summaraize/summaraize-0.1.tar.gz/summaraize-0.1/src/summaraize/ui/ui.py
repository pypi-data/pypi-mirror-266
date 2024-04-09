import sys
import queue
import threading
import logging
import dataclasses
import ttkbootstrap as ttk
from .ffmpeg_error_page import FfmpegErrorPage
from .api_key_page import ApiKeyPage
from .upload_recording_page import UploadRecordingPage
from .summarize_page import SummarisePage
from .show_summary_page import ShowSummaryPage
from ..summarize import Summarize

logger = logging.getLogger(__name__)
PAGES = {x.__name__:x for x in
         [FfmpegErrorPage, UploadRecordingPage,
          SummarisePage, ShowSummaryPage,
          ApiKeyPage]}


@dataclasses.dataclass
class Params:
    # pylint: disable=missing-function-docstring
    """
    Container for app params
    """
    _result: str=""
    _transcript: str=""
    _prompt_history: str=""
    _language: str=""

    @property
    def transcript(self) -> str:
        return self._transcript

    @transcript.setter
    def transcript(self, value: str):
        self._transcript = value

    @property
    def result(self) -> str:
        return self._result

    @result.setter
    def result(self, value: str):
        self._result = value

    @property
    def language(self) -> str:
        return self._language

    @language.setter
    def language(self, value: str):
        self._language = value

    @property
    def prompt_history(self) -> str:
        return self._prompt_history

    @prompt_history.setter
    def prompt_history(self, value: str):
        if self._prompt_history:
            self._prompt_history = value + \
                "\n\n-----------------------------\n\n" \
                 + self._prompt_history
        else:
            self._prompt_history = value + "\n\n"


class App(ttk.Window):
    """
    tkinter ui app for ai-minutes lib
    """
    def __init__(self, themename: str):
        super().__init__(themename=themename)
        self.task_queue = queue.Queue()
        self.result_queue = queue.Queue()
        try:
            self.summarize = Summarize(self.task_queue, self.result_queue)
        # pylint: disable=broad-exception-caught
        except Exception as e:
            logger.error("Failed to contact OpenAI: %s", str(e))
            sys.exit(1)
        self.title('Summarize Transcript')
        self.geometry("700x800")
        self._frame = None
        btn_style = ttk.Style()
        btn_style.configure("TButton", font=("Helvetica", 16, "bold"))
        try:
            self.summarize.check_ffmpeg_present()
        except RuntimeError:
            self.switch_frame(FfmpegErrorPage)
            return
        self.params = Params()
        self.worker_thread = threading.Thread(target=self.summarize.run)
        self.worker_thread.start()

        if self.summarize.client is None:
            self.switch_frame("ApiKeyPage")
        else:
            self.switch_frame("UploadRecordingPage")

    def switch_frame(self, frame_class_name: str) -> None:
        """Destroys current frame and replaces it with a new one."""
        try:
            frame_class = PAGES[frame_class_name]
        except KeyError:
            # pylint: disable=logging-fstring-interpolation
            logger.error(f"unknown page {frame_class_name}")
            sys.exit(1)
        new_frame = frame_class(self)
        if self._frame is not None:
            self._frame.destroy()
        self._frame = new_frame
        self._frame.pack()
