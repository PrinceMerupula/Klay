from PySide6.QtWidgets import (
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)
from PySide6.QtCore import QThread

from klay.downloader import download, is_valid_url
from klay.download_worker import DownloadWorker

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Klay")
        self.resize(800, 500)

        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Paste or enter a URL")

        self.download_button = QPushButton("Download")
        self.download_button.clicked.connect(self.handle_download)
        self.download_active = False

        layout = QVBoxLayout()
        layout.addWidget(self.url_input)
        layout.addWidget(self.download_button)

        container = QWidget()
        container.setLayout(layout)

        self.setCentralWidget(container)

    def handle_download(self):
        url = self.url_input.text().strip()

        if not url:
            QMessageBox.warning(
                self,
                "Missing URL",
                "Please enter a URL before downloading.",
            )
            return

        if not is_valid_url(url):
            QMessageBox.warning(
                self,
                "Invalid URL",
                "Please enter a valid HTTP or HTTPS URL.",
            )
            return

        self.download_active = True
        self.download_button.setEnabled(False)

        self.thread = QThread()
        self.worker = DownloadWorker(url)

        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)

        self.worker.finished.connect(self.download_finished)
        self.worker.failed.connect(self.download_failed)

        self.worker.finished.connect(self.thread.quit)
        self.worker.failed.connect(self.thread.quit)

        self.thread.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        self.thread.start()

    def download_finished(self):
        self.download_active = False
        self.download_button.setEnabled(True)

        QMessageBox.information(
            self,
            "Download Complete",
            "The download completed successfully.",
        )


    def download_failed(self):
        self.download_active = False
        self.download_button.setEnabled(True)

        QMessageBox.critical(
            self,
            "Download Failed",
            "Klay could not download media from this URL.",
        )

    def closeEvent(self, event):
        if self.download_active:
            QMessageBox.warning(
                self,
                "Download in Progress",
                "Please wait for the current download to finish before closing Klay.",
            )
            event.ignore()
            return

        event.accept()