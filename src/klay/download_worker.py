from PySide6.QtCore import QObject, Signal, Slot
from yt_dlp.utils import DownloadError

from klay.downloader import download


class DownloadWorker(QObject):
    finished = Signal()
    failed = Signal()

    def __init__(self, url: str):
        super().__init__()
        self.url = url

    @Slot()
    def run(self):
        try:
            download(self.url)
        except DownloadError:
            self.failed.emit()
        else:
            self.finished.emit()