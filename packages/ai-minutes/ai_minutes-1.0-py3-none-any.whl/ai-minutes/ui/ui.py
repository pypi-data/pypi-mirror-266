import sys
import queue
import threading
import logging
import ttkbootstrap as ttk
from ..summarize import Summarize
from .pages import (
    FfmpegErrorPage,
    ApiKeyPage,
    UploadRecordingPage
)

logger = logging.getLogger(__name__)


class App(ttk.Window):
    def __init__(self, themename: str):
        super().__init__(themename=themename)
        self.task_queue = queue.Queue()
        self.result_queue = queue.Queue()
        try:
            self.summarize = Summarize(self.task_queue, self.result_queue)
        except Exception as e:
            logger.error(f"Failed to contact OpenAI: {str(e)}")
            sys.exit(1)
        self.title('Summarize Transcript')
        self.geometry("700x800")
        self._frame = None
        btn_style = ttk.Style()
        btn_style.configure("TButton", font=("Helvetica", 16, "bold"))
        try:
            self.summarize.check_ffmpeg_present()
        except Exception:
            self.switch_frame(FfmpegErrorPage)
            return
        self._result = None
        self._transcript = None
        self._prompt_history = ""
        self._language = ""
        self.worker_thread = threading.Thread(target=self.summarize.run)
        self.worker_thread.start()

        if self.summarize.client is None:
            self.switch_frame(ApiKeyPage)
        else:
            self.switch_frame(UploadRecordingPage)

    def switch_frame(self, frame_class: type(ttk.Frame)) -> None:
        """Destroys current frame and replaces it with a new one."""
        new_frame = frame_class(self)
        if self._frame is not None:
            self._frame.destroy()
        self._frame = new_frame
        self._frame.pack()

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
            self._prompt_history = value + "\n\n-----------------------------\n\n" + self._prompt_history
        else:
            self._prompt_history = value + "\n\n"
