from PySide6.QtWidgets import (
    QLineEdit,
    QLabel,
    QMainWindow,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QVBoxLayout,
    QWidget,
)
from PySide6.QtCore import QThread

from klay.download_worker import DownloadWorker
from klay.analysis_worker import AnalysisWorker
from klay.downloader import is_valid_url

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Klay")
        self.resize(800, 500)

        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Paste or enter a URL")

        self.analyze_button = QPushButton("Analyze")
        self.analyze_button.clicked.connect(self.handle_analyze)

        self.title_label = QLabel("Title: —")
        self.uploader_label = QLabel("Uploader: —")
        self.duration_label = QLabel("Duration: —")
        self.resolution_label = QLabel("Best resolution: —")

        self.download_button = QPushButton("Download")
        self.download_button.clicked.connect(self.handle_download)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)

        self.download_active = False

        layout = QVBoxLayout()
        layout.addWidget(self.url_input)
        layout.addWidget(self.analyze_button)

        layout.addWidget(self.title_label)
        layout.addWidget(self.uploader_label)
        layout.addWidget(self.duration_label)
        layout.addWidget(self.resolution_label)
        
        layout.addWidget(self.download_button)
        layout.addWidget(self.progress_bar)

        container = QWidget()
        container.setLayout(layout)

        self.setCentralWidget(container)

    def handle_analyze(self):
        url = self.url_input.text().strip()

        if not url:
            QMessageBox.warning(
                self,
                "Missing URL",
                "Please enter a URL before analyzing.",
            )
            return

        if not is_valid_url(url):
            QMessageBox.warning(
                self,
                "Invalid URL",
                "Please enter a valid HTTP or HTTPS URL.",
            )
            return

        self.analyze_button.setEnabled(False)
        self.title_label.setText("Analyzing...")

        self.analysis_thread = QThread()
        self.analysis_worker = AnalysisWorker(url)

        self.analysis_worker.moveToThread(self.analysis_thread)

        self.analysis_thread.started.connect(self.analysis_worker.run)

        self.analysis_worker.finished.connect(self.analysis_finished)
        self.analysis_worker.failed.connect(self.analysis_failed)

        self.analysis_worker.finished.connect(self.analysis_thread.quit)
        self.analysis_worker.failed.connect(self.analysis_thread.quit)

        self.analysis_worker.finished.connect(self.analysis_worker.deleteLater)
        self.analysis_worker.failed.connect(self.analysis_worker.deleteLater)

        self.analysis_thread.finished.connect(self.analysis_thread.deleteLater)

        self.analysis_thread.start()

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
        self.progress_bar.setValue(0)

        self.thread = QThread()
        self.worker = DownloadWorker(url)

        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)

        self.worker.progress.connect(self.update_progress)
        self.worker.finished.connect(self.download_finished)
        self.worker.failed.connect(self.download_failed)

        self.worker.finished.connect(self.thread.quit)
        self.worker.failed.connect(self.thread.quit)

        self.worker.finished.connect(self.worker.deleteLater)
        self.worker.failed.connect(self.worker.deleteLater)

        self.thread.finished.connect(self.thread.deleteLater)

        self.thread.start()

    def update_progress(self, percentage):
        self.progress_bar.setValue(percentage)

    def analysis_finished(self, info):
        self.analyze_button.setEnabled(True)

        title = info.get("title") or "Unknown title"
        uploader = (
            info.get("uploader")
            or info.get("channel")
            or "Unknown uploader"
        )

        duration = self.format_duration(info.get("duration"))

        formats = info.get("formats", [])

        heights = [
            format_info.get("height")
            for format_info in formats
            if format_info.get("height")
        ]

        best_height = max(heights) if heights else None

        resolution = (
            f"{best_height}p"
            if best_height
            else "Unknown"
        )

        self.title_label.setText(f"Title: {title}")
        self.uploader_label.setText(f"Uploader: {uploader}")
        self.duration_label.setText(f"Duration: {duration}")
        self.resolution_label.setText(
            f"Best resolution: {resolution}"
        )

    def analysis_failed(self):
        self.analyze_button.setEnabled(True)

        self.title_label.setText("Title: —")
        self.uploader_label.setText("Uploader: —")
        self.duration_label.setText("Duration: —")
        self.resolution_label.setText("Best resolution: —")

        QMessageBox.critical(
            self,
            "Analysis Failed",
            "Klay could not retrieve information for this URL.",
        )

    def format_duration(self, seconds):
        if seconds is None:
            return "Unknown"

        minutes, seconds = divmod(int(seconds), 60)
        hours, minutes = divmod(minutes, 60)

        if hours:
            return f"{hours}:{minutes:02}:{seconds:02}"

        return f"{minutes}:{seconds:02}"

    def download_finished(self):
        self.download_active = False
        self.download_button.setEnabled(True)
        self.progress_bar.setValue(100)

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