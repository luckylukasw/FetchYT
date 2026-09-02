"""Signal file

Handles download signals for updating progress, previews and log.
"""

from PySide6.QtCore import QObject, Signal

class DownloadSignals(QObject):
    progress = Signal(float, str)
    log = Signal(str)
    finished = Signal(bool, str)
    preview_loaded = Signal(dict)
    preview_failed = Signal(str)