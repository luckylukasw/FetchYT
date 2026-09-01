from PySide6.QtCore import QObject, Signal

class DownloadSignals(QObject):
    progress = Signal(float, str)
    log = Signal(str)
    finished = Signal(bool, str)
    preview_loaded = Signal(dict)   # Emits metadata dict (title, author, thumbnail_data)
    preview_failed = Signal(str)    # Emits error message if preview fails