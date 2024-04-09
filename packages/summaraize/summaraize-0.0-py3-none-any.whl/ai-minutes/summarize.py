"""
Module to analyze meeting recording with AI
"""
import queue
from tempfile import TemporaryDirectory
from subprocess import Popen, PIPE
import os
import logging
from openai import OpenAI, AuthenticationError

SYSTEM_MESSAGE = """
You are an assistant analysing a transcript from an event.
Analyze the transcript and provide the summary or answer to user as instructed or asked by user.
The language of the transcript should be {language}.
Provide the output in same language unless instructed otherwise.
"""

logger = logging.getLogger(__name__)


class Summarize:
    """
    Convert a video recording to a summary transcript and use the OpenAI API to
    analyze it.
    FFmpeg needs to be installed and set in path
    """
    def __init__(self,
        task_queue: queue.Queue | None = None,
        result_queue:queue.Queue | None = None
    ) -> None:
        self.task_queue = task_queue
        self.result_queue = result_queue
        self.running = True
        self.transcript = ""
        self.client: OpenAI | None = None
        if os.environ.get("OPENAI_API_KEY") is not None:
            try:
                client = OpenAI()
                client.models.list()
                self.client = client
            except AuthenticationError as e:
                # do not exit with wrong auth token, ask a new one
                logger.exception(e)
                del os.environ["OPENAI_API_KEY"]

    def run(self):
        """
        enables running methods inside a thread.
        only one main thread is calling
        for multithread apps, refactor needed
        """
        if self.task_queue is None or self.result_queue is None:
            raise AttributeError("No task queue or result queue")
        while self.running:
            # Retrieve a task from the queue
            task = self.task_queue.get()
            if task is None:  # Stop signal
                self.running = False
                self.task_queue.task_done()
                continue
            method_name, args, kwargs = task
            if hasattr(self, method_name):
                method = getattr(self, method_name)
                # Execute the method with the provided arguments
                try:
                    result = method(*args, **kwargs)
                    self.result_queue.put(result)
                # pylint: disable=broad-exception-caught
                except Exception as e:
                    logger.exception(e)
                    self.result_queue.put(e)
            else:
                logger.error("No method found for %s", method_name)

            self.task_queue.task_done()

    @staticmethod
    def check_ffmpeg_present():
        """
        Check FFmpeg installed in system and set in path.
        """
        with Popen(["ffmpeg", "-version"], stdout=PIPE, stderr=PIPE) as p:
            output, error = p.communicate()
            if p.returncode != 0:
                logger.error("FFmpeg error: %s, %s", output, error)
                raise RuntimeError(f"FFmpeg error, exiting: {error}")

    def _report(self, value: any):
        if self.result_queue is not None:
            self.result_queue.put(value)

    def _extract(self, video_file_path: str, audiofile: str) -> None:
        """
        extract audio track from video recording
        """
        cmd = ["ffmpeg", "-i", f"{video_file_path}",
               "-map", "0:a", "-c", "copy", f"{audiofile}"]
        with Popen(cmd, stdout=PIPE, stderr=PIPE) as p:
            _, error = p.communicate()
            if p.returncode != 0:
                raise RuntimeError(f"Failed to extract audio: {error}")

    def _chunk(self, audiofile: str, outfile: str, chunk_time: int) -> None:
        """
        chunk audio to match Whisper model context window
        """
        cmd = ["ffmpeg", "-i", f"{audiofile}",
               "-f", "segment", "-segment_time",
               f"{chunk_time}", f"{outfile}"]
        with Popen(cmd, stdout=PIPE, stderr=PIPE) as p:
            _, error = p.communicate()
            if p.returncode != 0:
                raise RuntimeError(f"Failed to chunk audio: {error}")

    def _speech_to_text(self, tmpdirname: str, language: str) -> str:
        """
        extract audio transcript from recording with OpenAI Whisper
        """
        transcript = ""
        audio_file_list = \
            sorted([fname for fname in os.listdir(tmpdirname) if fname.startswith("out_")])
        increment_step = 70 // len(audio_file_list)
        progress = 30
        for chunk_file_name in audio_file_list:
            fn = os.path.join(tmpdirname, chunk_file_name)
            with open(fn, "rb") as audio_file:
                transcript += self.client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    language=language,
                    response_format="text"
                )
            progress += increment_step
            self._report(progress)
        return transcript

    def set_api_key(self, api_key: str) -> None:
        """
        set and check user key authenticates
        """
        client = OpenAI(api_key=api_key)
        client.models.list()
        self.client = client

    def convert(self, video_file_path: str, chunk_time: int = 1200, language: str = "en") -> str:
        """
        extract audio track from a video recording and convert it 
        to a text transcript using OpenAI Whisper speech to text
        model and ffmpeg.

        :param video_file_path: str; path to video recording
        :param chunk_time: int; chunk time in seconds to extract audio
        :param language: str; language code of the recording:
            https://en.wikipedia.org/wiki/List_of_ISO_639_language_codes
        :return: str; transcript
        """
        transcript = ""
        with TemporaryDirectory(ignore_cleanup_errors=True) as tmpdirname:
            self.result_queue.put(5)
            audiofile = os.path.join(tmpdirname, "audio_track.m4a")
            self._extract(video_file_path, audiofile)
            self._report(15)
            # audio needs to be chunked to match Whisper model context window
            outfile = os.path.join(tmpdirname, "out_%03d.m4a")
            self._chunk(audiofile, outfile, chunk_time)
            self._report(30)
            transcript = self._speech_to_text(tmpdirname, language)
        self.transcript = transcript
        return transcript

    def summarize(self, prompt: str, language: str = "English") -> str:
        """
        Summarize the transcript according to instructions in prompts with GPT4-turbo
        :param prompt: str; the prompt to GPT4-Turbo model
        :param language: str; language name of the transcript:
            https://en.wikipedia.org/wiki/List_of_ISO_639_language_codes
        :return: str; the summary of the transcript
        """
        template = f"""
        {prompt}
        Transcript:
        {self.transcript}
        """
        chat_completion = self.client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": SYSTEM_MESSAGE.format(language=language)
                },
                {
                    "role": "user",
                    "content": template
                }
            ],
            model="gpt-4-turbo-preview"
        )
        return chat_completion.choices[0].message.content
