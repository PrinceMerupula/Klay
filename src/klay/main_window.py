from pathlib import Path

from PySide6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QVBoxLayout,
    QWidget,
)
from PySide6.QtCore import (
    QDir,
    QSettings, 
    QStandardPaths, 
    QThread,
    QUrl,
)

from PySide6.QtGui import QDesktopServices

from klay.analysis_worker import AnalysisWorker
from klay.download_worker import DownloadWorker
from klay.downloader import is_valid_url
from klay.dependencies import is_ffmpeg_available


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Klay")
        self.resize(800, 500)

        self.settings = QSettings("Klay", "Klay")

        self.default_output_directory = QStandardPaths.writableLocation(
            QStandardPaths.DownloadLocation
        )

        if not self.default_output_directory:
            self.default_output_directory = QStandardPaths.writableLocation(
                QStandardPaths.HomeLocation
            )

        self.output_directory = self.load_output_directory()
        self.last_downloaded_file = None
        self.analyzed_url = None

        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Paste or enter a URL")
        self.url_input.textChanged.connect(self.handle_url_changed)

        self.analyze_button = QPushButton("Analyze")
        self.analyze_button.clicked.connect(self.handle_analyze)

        self.title_label = QLabel("Title: —")
        self.uploader_label = QLabel("Uploader: —")
        self.duration_label = QLabel("Duration: —")
        self.resolution_label = QLabel("Best resolution: —")

        self.folder_button = QPushButton("Choose Download Folder")
        self.folder_button.clicked.connect(self.choose_output_directory)

        self.folder_label = QLabel(
            f"Download folder: {self.output_directory}"
        )

        self.format_selector = QComboBox()
        self.format_selector.addItems([
            "Video + Audio",
            "Video Only",
            "Audio Only",
        ])

        saved_download_mode = self.settings.value(
            "download_mode",
            "Video + Audio",
        )

        if self.format_selector.findText(saved_download_mode) >= 0:
            self.format_selector.setCurrentText(saved_download_mode)

        self.quality_selector = QComboBox()
        self.quality_selector.addItem("Best Available")

        self.audio_format_selector = QComboBox()
        self.audio_format_selector.addItems([
            "Original",
            "MP3",
            "M4A",
        ])

        saved_audio_format = self.settings.value(
            "audio_format",
            "Original",
        )

        if self.audio_format_selector.findText(saved_audio_format) >= 0:
            self.audio_format_selector.setCurrentText(saved_audio_format)

        self.format_selector.currentTextChanged.connect(
            self.update_download_options
        )
        self.format_selector.currentTextChanged.connect(
            self.save_download_mode
        )
        self.audio_format_selector.currentTextChanged.connect(
            self.save_audio_format
        )

        self.update_download_options(
            self.format_selector.currentText()
        )

        self.download_button = QPushButton("Download")
        self.download_button.clicked.connect(self.handle_download)

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.handle_cancel)
        self.cancel_button.setEnabled(False)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)

        self.download_active = False
        self.analysis_active = False

        layout = QVBoxLayout()

        layout.addWidget(self.url_input)
        layout.addWidget(self.analyze_button)

        layout.addWidget(self.title_label)
        layout.addWidget(self.uploader_label)
        layout.addWidget(self.duration_label)
        layout.addWidget(self.resolution_label)

        layout.addWidget(self.folder_button)
        layout.addWidget(self.folder_label)

        layout.addWidget(self.format_selector)
        layout.addWidget(self.quality_selector)
        layout.addWidget(self.audio_format_selector)
        layout.addWidget(self.download_button)
        layout.addWidget(self.cancel_button)
        layout.addWidget(self.progress_bar)

        container = QWidget()
        container.setLayout(layout)

        self.setCentralWidget(container)

    def handle_url_changed(self):
        self.analyzed_url = None

        self.title_label.setText("Title: —")
        self.uploader_label.setText("Uploader: —")
        self.duration_label.setText("Duration: —")
        self.resolution_label.setText("Best resolution: —")

        self.quality_selector.clear()
        self.quality_selector.addItem("Best Available")

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

        if self.download_active:
            QMessageBox.warning(
                self,
                "Download in Progress",
                "Please wait for the current download to finish before analyzing.",
            )
            return

        self.analysis_active = True
        self.analyze_button.setEnabled(False)
        self.title_label.setText("Analyzing...")
        self.analyzed_url = url

        self.analysis_thread = QThread()
        self.analysis_worker = AnalysisWorker(url)

        self.analysis_worker.moveToThread(self.analysis_thread)

        self.analysis_thread.started.connect(self.analysis_worker.run)

        self.analysis_worker.finished.connect(self.analysis_finished)
        self.analysis_worker.failed.connect(self.analysis_failed)

        self.analysis_worker.finished.connect(self.analysis_thread.quit)
        self.analysis_worker.failed.connect(self.analysis_thread.quit)

        self.analysis_worker.finished.connect(
            self.analysis_worker.deleteLater
        )
        self.analysis_worker.failed.connect(
            self.analysis_worker.deleteLater
        )

        self.analysis_thread.finished.connect(
            self.analysis_thread.deleteLater
        )

        self.analysis_thread.start()

    def load_output_directory(self):
        saved_directory = self.settings.value(
            "output_directory",
            self.default_output_directory,
        )

        if saved_directory and QDir(saved_directory).exists():
            return saved_directory

        return self.default_output_directory

    def save_download_mode(self, download_mode):
        self.settings.setValue(
            "download_mode",
            download_mode,
        )

    def save_audio_format(self, audio_format):
        self.settings.setValue(
            "audio_format",
            audio_format,
        )

    def choose_output_directory(self):
        directory = QFileDialog.getExistingDirectory(
            self,
            "Choose Download Folder",
        )

        if directory:
            self.output_directory = directory
            self.settings.setValue(
                "output_directory",
                directory,
            )
            self.folder_label.setText(
                f"Download folder: {directory}"
            )

    def update_download_options(self, download_mode):
        audio_only = download_mode == "Audio Only"

        self.quality_selector.setEnabled(not audio_only)
        self.audio_format_selector.setEnabled(audio_only)

    def download_requires_ffmpeg(self):
        download_mode = self.format_selector.currentText()
        audio_format = self.audio_format_selector.currentText()

        if download_mode == "Video + Audio":
            return True

        if download_mode == "Audio Only":
            return audio_format in ("MP3", "M4A")

        return False

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

        if self.analysis_active:
            QMessageBox.warning(
                self,
                "Analysis in Progress",
                "Please wait for the current analysis to finish before downloading.",
            )
            return

        if self.download_requires_ffmpeg() and not is_ffmpeg_available():
            QMessageBox.warning(
                self,
                "FFmpeg Not Found",
                (
                    "FFmpeg is required for this download option.\n\n"
                    "Install FFmpeg and restart Klay before trying again."
                ),
            )
            return

        download_mode = self.format_selector.currentText()
        audio_format = self.audio_format_selector.currentText()

        selected_quality = self.quality_selector.currentText()

        if selected_quality == "Best Available":
            max_height = None
        else:
            max_height = int(selected_quality.removesuffix("p"))

        self.download_active = True
        self.download_button.setEnabled(False)
        self.cancel_button.setEnabled(True)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)

        self.thread = QThread()
        self.worker = DownloadWorker(
            url,
            self.output_directory,
            download_mode,
            max_height,
            audio_format,
        )

        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)

        self.worker.progress.connect(self.update_progress)
        self.worker.processing.connect(self.download_processing)
        self.worker.finished.connect(self.download_finished)
        self.worker.failed.connect(self.download_failed)
        self.worker.canceled.connect(self.download_canceled)

        self.worker.finished.connect(self.thread.quit)
        self.worker.failed.connect(self.thread.quit)
        self.worker.canceled.connect(self.thread.quit)

        self.worker.finished.connect(self.worker.deleteLater)
        self.worker.failed.connect(self.worker.deleteLater)
        self.worker.canceled.connect(self.worker.deleteLater)

        self.thread.finished.connect(self.thread.deleteLater)

        self.thread.start()

    def update_progress(self, percentage):
        self.progress_bar.setValue(percentage)

    def download_processing(self):
        self.progress_bar.setRange(0, 0)

    def handle_cancel(self):
        if not self.download_active:
            return

        self.cancel_button.setEnabled(False)
        self.worker.request_cancel()

    def analysis_finished(self, info):
        self.analysis_active = False
        self.analyze_button.setEnabled(True)

        if self.url_input.text().strip() != self.analyzed_url:
            return

        title = info.get("title") or "Unknown title"

        uploader = (
            info.get("uploader")
            or info.get("channel")
            or "Unknown uploader"
        )

        duration = self.format_duration(
            info.get("duration")
        )

        formats = info.get("formats", [])

        heights = {
            format_info.get("height")
            for format_info in formats
            if format_info.get("height")
        }

        available_heights = sorted(
            heights,
            reverse=True,
        )

        best_height = (
            available_heights[0]
            if available_heights
            else None
        )

        resolution = (
            f"{best_height}p"
            if best_height
            else "Unknown"
        )

        self.quality_selector.clear()
        self.quality_selector.addItem("Best Available")

        for height in available_heights:
            self.quality_selector.addItem(
                f"{height}p"
            )

        self.title_label.setText(
            f"Title: {title}"
        )
        self.uploader_label.setText(
            f"Uploader: {uploader}"
        )
        self.duration_label.setText(
            f"Duration: {duration}"
        )
        self.resolution_label.setText(
            f"Best resolution: {resolution}"
        )

    def analysis_failed(self):
        self.analysis_active = False
        self.analyze_button.setEnabled(True)

        self.title_label.setText("Title: —")
        self.uploader_label.setText("Uploader: —")
        self.duration_label.setText("Duration: —")
        self.resolution_label.setText(
            "Best resolution: —"
        )

        self.quality_selector.clear()
        self.quality_selector.addItem("Best Available")

        QMessageBox.critical(
            self,
            "Analysis Failed",
            "Klay could not retrieve information for this URL.",
        )

    def format_duration(self, seconds):
        if seconds is None:
            return "Unknown"

        minutes, seconds = divmod(
            int(seconds),
            60,
        )
        hours, minutes = divmod(
            minutes,
            60,
        )

        if hours:
            return (
                f"{hours}:"
                f"{minutes:02}:"
                f"{seconds:02}"
            )

        return f"{minutes}:{seconds:02}"

    def download_finished(self, final_filepath):
        self.download_active = False
        self.download_button.setEnabled(True)
        self.cancel_button.setEnabled(False)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(100)

        self.last_downloaded_file = final_filepath

        if final_filepath:
            final_path = Path(final_filepath)

            message = (
                "The download completed successfully.\n\n"
                f"{final_path.name}\n\n"
                f"Saved to:\n{final_path.parent}"
            )
        else:
            message = "The download completed successfully."

        message_box = QMessageBox(self)
        message_box.setWindowTitle("Download Complete")
        message_box.setText(message)

        open_file_button = None
        show_folder_button = None

        if final_filepath:
            open_file_button = message_box.addButton(
                "Open File",
                QMessageBox.ActionRole,
            )

            show_folder_button = message_box.addButton(
                "Show in Folder",
                QMessageBox.ActionRole,
            )

        message_box.addButton(
            QMessageBox.Ok,
        )

        message_box.exec()

        clicked_button = message_box.clickedButton()

        if clicked_button == open_file_button:
            self.open_last_downloaded_file()
        elif clicked_button == show_folder_button:
            self.show_last_download_in_folder()

    def download_failed(self):
        self.download_active = False
        self.download_button.setEnabled(True)
        self.cancel_button.setEnabled(False)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)

        QMessageBox.critical(
            self,
            "Download Failed",
            "Klay could not download media from this URL.",
        )

    def download_canceled(self):
        self.download_active = False
        self.download_button.setEnabled(True)
        self.cancel_button.setEnabled(False)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)

        QMessageBox.information(
            self,
            "Download Canceled",
            "The download was canceled.",
        )

    def open_last_downloaded_file(self):
        if not self.last_downloaded_file:
            return

        file_path = Path(self.last_downloaded_file)

        if not file_path.exists():
            QMessageBox.warning(
                self,
                "File Not Found",
                "The downloaded file could not be found.",
            )
            return

        opened = QDesktopServices.openUrl(
            QUrl.fromLocalFile(str(file_path))
        )

        if not opened:
            QMessageBox.warning(
                self,
                "Unable to Open File",
                "Klay could not open the downloaded file.",
            )

    def show_last_download_in_folder(self):
        if not self.last_downloaded_file:
            return

        file_path = Path(self.last_downloaded_file)
        folder_path = file_path.parent

        if not folder_path.exists():
            QMessageBox.warning(
                self,
                "Folder Not Found",
                "The download folder could not be found.",
            )
            return

        opened = QDesktopServices.openUrl(
            QUrl.fromLocalFile(str(folder_path))
        )

        if not opened:
            QMessageBox.warning(
                self,
                "Unable to Open Folder",
                "Klay could not open the download folder.",
            )

    def closeEvent(self, event):
        if self.analysis_active:
            QMessageBox.warning(
                self,
                "Analysis in Progress",
                "Please wait for the current analysis to finish before closing Klay.",
            )
            event.ignore()
            return
        if self.download_active:
            QMessageBox.warning(
                self,
                "Download in Progress",
                "Please wait for the current download to finish before closing Klay.",
            )
            event.ignore()
            return

        event.accept()