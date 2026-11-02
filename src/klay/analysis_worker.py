import logging

from PySide6.QtCore import QObject, Signal, Slot

from klay.downloader import get_media_info

logger = logging.getLogger(__name__)


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
        except Exception:
            logger.exception("Analysis failed")
            self.failed.emit()
        else:
            self.finished.emit(info)