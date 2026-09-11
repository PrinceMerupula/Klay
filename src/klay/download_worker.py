from PySide6.QtCore import QObject, Signal, Slot
from yt_dlp.utils import DownloadError

from klay.downloader import download


class DownloadWorker(QObject):
    finished = Signal()
    failed = Signal()
    progress = Signal(int)

    def __init__(self, url: str):
        super().__init__()
        self.url = url

    @Slot()
    def run(self):
        try:
            download(self.url, self.handle_progress)
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