"""UI for FetchYT application window

This module defines the MainWindow widget, managing URL inputs, video preview
rendering, format selection, progress tracking, and log display.
"""

from __future__ import annotations

import os
import threading
from typing import Any

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QLabel,
    QFileDialog,
    QProgressBar,
    QTextEdit,
    QComboBox,
    QFrame,
    QMessageBox
)


from core.downloader import VideoDownloadService
from core.signals import DownloadSignals
from styles import THEME

class MainWindow(QWidget):
    """Main application window

    Attributes:
        signals: Signal hub managing download events.
        download_service: Service handling asynchronous download operations.
        download_dir: Target filesystem path for saved files.
        url_debounce_timer: Timer delaying preview fetch requests on input changes.
    """
    def __init__(self):
        """Initialize the main window, services, timers, and UI components."""
        super().__init__()
        self.setStyleSheet(THEME)

        self.signals = DownloadSignals()
        self.download_service = VideoDownloadService(self.signals)
        self.download_dir = os.path.expanduser("~/Downloads")

        # Debounce timer for URL typing/pasting
        self.url_debounce_timer = QTimer()
        self.url_debounce_timer.setSingleShot(True)
        self.url_debounce_timer.setInterval(750)
        self.url_debounce_timer.timeout.connect(self.trigger_preview_fetch)

        self._bind_signals()
        self._init_ui()

    def _bind_signals(self):
        """Connect internal signals to their respective slot handlers."""
        self.signals.progress.connect(self.on_progress)
        self.signals.log.connect(self.append_log)
        self.signals.finished.connect(self.on_finished)
        self.signals.preview_loaded.connect(self.display_preview)
        self.signals.preview_failed.connect(self.on_preview_failed)

    def _init_ui(self):
        """Construct and layout all UI widgets in the window."""
        self.setWindowTitle("FetchYT")
        self.resize(540, 600)

        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)

        # URL Input
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Paste YouTube URL here...")
        self.url_input.textChanged.connect(lambda: self.url_debounce_timer.start())
        layout.addWidget(self.url_input)

        # Video Preview Card (Title -> Subtitle -> Thumbnail)
        self.preview_card = QFrame()
        self.preview_card.setObjectName("previewCard")
        self.preview_card.setVisible(False)
        preview_layout = QVBoxLayout(self.preview_card)
        preview_layout.setSpacing(8)

        self.title_label = QLabel("Video Title")
        self.title_label.setStyleSheet("font-weight: bold; font-size: 13px;")
        self.title_label.setWordWrap(True)
        preview_layout.addWidget(self.title_label)

        self.details_label = QLabel("Channel • Duration")
        self.details_label.setStyleSheet("color: #94a3b8; font-size: 11px;")
        preview_layout.addWidget(self.details_label)

        self.thumb_label = QLabel()
        self.thumb_label.setFixedHeight(180)
        self.thumb_label.setAlignment(Qt.AlignCenter)
        self.thumb_label.setStyleSheet("border-radius: 6px; background-color: transparent;")
        preview_layout.addWidget(self.thumb_label)

        layout.addWidget(self.preview_card)

        # Folder Destination Selector
        folder_layout = QHBoxLayout()
        self.folder_label = QLineEdit(self.download_dir)
        self.folder_label.setReadOnly(True)
        self.browse_btn = QPushButton("Browse...")
        self.browse_btn.setObjectName("browseBtn")
        self.browse_btn.clicked.connect(self.choose_folder)
        folder_layout.addWidget(self.folder_label)
        folder_layout.addWidget(self.browse_btn)
        layout.addLayout(folder_layout)

        # Format Selector
        format_layout = QHBoxLayout()
        format_label = QLabel("Format:")
        format_label.setStyleSheet("color: #94a3b8; font-weight: 500;")
        self.format_combo = QComboBox()
        self.format_combo.addItems(["Video (MP4)", "Audio Only (MP3)"])
        format_layout.addWidget(format_label)
        format_layout.addWidget(self.format_combo)
        layout.addLayout(format_layout)

        # Progress Bar & Status Readout
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)

        self.status_label = QLabel("Ready", alignment=Qt.AlignCenter)
        self.status_label.setWordWrap(True)
        self.status_label.setStyleSheet("color: #94a3b8;")
        layout.addWidget(self.status_label)

        # Action Buttons
        btn_layout = QHBoxLayout()
        self.submit_btn = QPushButton("Download")
        self.submit_btn.clicked.connect(self.start_download)

        self.about_btn = QPushButton("About")
        self.about_btn.setObjectName("aboutBtn")
        self.about_btn.clicked.connect(self.show_about_dialog)

        self.toggle_logs_btn = QPushButton("Show Logs")
        self.toggle_logs_btn.setObjectName("logToggleBtn")
        self.toggle_logs_btn.clicked.connect(self.toggle_logs)

        btn_layout.addWidget(self.submit_btn)
        btn_layout.addWidget(self.toggle_logs_btn)
        btn_layout.addWidget(self.about_btn)
        layout.addLayout(btn_layout)

        # Collapsible Logs Panel
        self.log_view = QTextEdit()
        self.log_view.setReadOnly(True)
        self.log_view.setVisible(False)
        self.log_view.setFixedHeight(120)
        layout.addWidget(self.log_view)

    def trigger_preview_fetch(self):
        """Validate input URL and spawn a thread to fetch metadata."""
        # Strip all white spaces...
        url = self.url_input.text().strip()

        # Validate if url is from YouTube. Safety measure that doesn't fetch metadata from other sites
        if "youtube.com/watch" in url or "youtu.be/" in url:
            self.status_label.setText("Fetching video preview...")
            threading.Thread(
                target=self.download_service.fetch_preview,
                args=(url,),
                daemon=True
            ).start()
        else:
            self.preview_card.setVisible(False)

    def show_about_dialog(self):
        """Display the application information and third-party license notices."""
        QMessageBox.about(
            self,
            "About FetchYT",
            "<h3>FetchYT</h3>"
            "<p>A simple, ad-free YouTube downloader.</p>"
            "<hr>"
            "<b>Third-Party Libraries & Licenses:</b>"
            "<ul>"
            "<li><b>yt-dlp:</b> The Unlicense (Public Domain)</li>"
            "<li><b>FFmpeg:</b> GNU LGPL v2.1+ / GPL</li>"
            "<li><b>PySide6 / Qt:</b> GNU LGPL v3</li>"
            "<li><b>Node.js:</b> MIT License</li>"
            "<li><b>imageio-ffmpeg:</b> BSD 2-Clause</li>"
            "</ul>"
            "<p><small>See included <code>THIRD_PARTY_LICENSES.txt</code> for full details.</small></p>"
            "<p>For errors, see FAQ, most answers are found there! :D</p>"
        )

    def display_preview(self, meta: dict):
        """Populate and display the preview card with metadata.

        Args:
            meta: Dictionary containing video attributes such as 'title',
                'uploader', 'duration', and binary 'image_data'.
        """
        self.title_label.setText(meta.get('title', ''))
        self.details_label.setText(f"{meta.get('uploader', '')} • {meta.get('duration', '')}")

        image_bytes = meta.get('image_data')
        if image_bytes:
            pixmap = QPixmap()
            if pixmap.loadFromData(image_bytes):
                scaled = pixmap.scaled(
                    480, 180,
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )
                self.thumb_label.setPixmap(scaled)
            else:
                self.thumb_label.setText("Could not display thumbnail")
        else:
            self.thumb_label.setText("No thumbnail available")

        self.preview_card.setVisible(True)
        self.status_label.setText("Ready to download.")

    def on_preview_failed(self, error: str):
        """Handle preview fetching failures.

        Args:
            error: Error message or reason for the fetch failure.
        """
        self.preview_card.setVisible(False)
        self.status_label.setText(f"Could not load preview: {error}")

    def choose_folder(self):
        """Open a directory picker dialog to select the download path."""
        folder = QFileDialog.getExistingDirectory(self, "Select Directory", self.download_dir)
        if folder:
            self.download_dir = folder
            self.folder_label.setText(folder)

    def toggle_logs(self):
        """Toggle visibility of the collapsible log panel."""
        is_visible = self.log_view.isVisible()
        self.log_view.setVisible(not is_visible)
        self.toggle_logs_btn.setText("Hide Logs" if not is_visible else "Show Logs")

    def start_download(self):
        """Validate input parameters and trigger asynchronous video download."""
        url = self.url_input.text().strip()
        if not url:
            self.status_label.setText("URL cannot be empty.")
            return

        self.submit_btn.setEnabled(False)
        self.progress_bar.setValue(0)
        self.status_label.setText("Initializing download...")
        self.log_view.clear()

        audio_only = self.format_combo.currentText() == "Audio Only (MP3)"

        threading.Thread(
            target=self.download_service.download,
            args=(url, self.download_dir, audio_only),
            daemon=True
        ).start()

    def on_progress(self, percent: float, text: str):
        """Update progress bar and status readout during active downloads.

        Args:
            percent: Download percentage (0 to 100).
            text: Status string description (e.g., speed, ETA).
        """
        self.progress_bar.setValue(int(percent))
        self.status_label.setText(text)

    def append_log(self, text: str):
        """Append log output to the collapsible log text area.

        Args:
            text: Log message string to append.
        """
        self.log_view.append(text)

    def on_finished(self, success: bool, message: str):
        """Handle download completion or termination.

        Args:
            success: Whether the download succeeded.
            message: Completion status message to display.
        """
        self.submit_btn.setEnabled(True)
        self.status_label.setText(message)
        self.progress_bar.setValue(100 if success else 0)