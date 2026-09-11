from PySide6.QtWidgets import (
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from yt_dlp.utils import DownloadError

from klay.downloader import download, is_valid_url

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Klay")
        self.resize(800, 500)

        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Paste or enter a URL")

        self.download_button = QPushButton("Download")
        self.download_button.clicked.connect(self.handle_download)

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

        try:
            download(url)
        except DownloadError:
            QMessageBox.critical(
                self,
                "Download Failed",
                "Klay could not download media from this URL.",
            )