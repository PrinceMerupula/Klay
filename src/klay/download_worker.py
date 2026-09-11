from PySide6.QtCore import QObject, Signal, Slot
from yt_dlp.utils import DownloadError

from klay.downloader import download


class DownloadWorker(QObject):
    finished = Signal()
    failed = Signal()
    progress = Signal(int)

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

    @Slot()
    def run(self):
        try:
            download(
                self.url,
                progress_hook=self.handle_progress,
                output_directory=self.output_directory,
                download_mode=self.download_mode,
                max_height=self.max_height,
                audio_format=self.audio_format,
            )
        except DownloadError:
            self.failed.emit()
        else:
            self.finished.emit()

    def handle_progress(self, data):
        if data["status"] != "downloading":
            return

        downloaded_bytes = data.get("downloaded_bytes", 0)

        total_bytes = (
            data.get("total_bytes")
            or data.get("total_bytes_estimate")
        )

        if total_bytes:
            percentage = int((downloaded_bytes / total_bytes) * 100)
            self.progress.emit(percentage)