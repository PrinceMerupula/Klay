from PySide6.QtWidgets import (
    QLineEdit,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from klay.downloader import download

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
        url = self.url_input.text()
        download(url)