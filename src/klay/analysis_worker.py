from PySide6.QtCore import QObject, Signal, Slot
from yt_dlp.utils import DownloadError

from klay.downloader import get_media_info


class AnalysisWorker(QObject):
    finished = Signal(dict)
    failed = Signal()

    def __init__(self, url: str):
        super().__init__()
        self.url = url

    @Slot()
    def run(self):
        try:
            info = get_media_info(self.url)
        except DownloadError:
            self.failed.emit()
        else:
            self.finished.emit(info)