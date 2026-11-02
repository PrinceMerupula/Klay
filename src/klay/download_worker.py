import logging
from threading import Event

from PySide6.QtCore import QObject, Signal, Slot

from klay.downloader import DownloadCanceled, download

logger = logging.getLogger(__name__)


class DownloadWorker(QObject):
    finished = Signal(object)
    failed = Signal()
    canceled = Signal()
    progress = Signal(int)
    processing = Signal()

    def __init__(
        self,
        url: str,
        output_directory=None,
        download_mode="Video + Audio",
        max_height=None,
        audio_format="Original",
    ):
        super().__init__()

        self.url = url
        self.output_directory = output_directory
        self.download_mode = download_mode
        self.max_height = max_height
        self.audio_format = audio_format

        self.cancel_event = Event()

    def request_cancel(self):
        self.cancel_event.set()
    
    @Slot()
    def run(self):
        if self.cancel_event.is_set():
            self.canceled.emit()
            return
        
        try:
            final_filepath = download(
                self.url,
                progress_hook=self.handle_progress,
                output_directory=self.output_directory,
                download_mode=self.download_mode,
                max_height=self.max_height,
                audio_format=self.audio_format,
            )
        except DownloadCanceled:
            self.canceled.emit()
        except Exception:
            logger.exception("Download failed")
            self.failed.emit()
        else:
            self.finished.emit(final_filepath)

    def handle_progress(self, data):
        if self.cancel_event.is_set():
            raise DownloadCanceled()

        status = data.get("status")

        if status == "finished":
            self.processing.emit()
            return

        if status != "downloading":
            return

        downloaded_bytes = data.get("downloaded_bytes", 0)

        total_bytes = (
            data.get("total_bytes")
            or data.get("total_bytes_estimate")
        )

        if total_bytes:
            percentage = int((downloaded_bytes / total_bytes) * 100)
            self.progress.emit(percentage)