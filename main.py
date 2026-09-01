import sys
import os
import ctypes
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon
from ui.main_window import MainWindow


def get_platform_icon() -> QIcon:
    """Returns .ico on Windows and .png on Linux/macOS."""
    base_dir = os.path.dirname(os.path.abspath(__file__))

    if sys.platform == "win32":
        icon_path = os.path.join(base_dir, "assets/icon.ico")
    else:
        icon_path = os.path.join(base_dir, "assets/icon.png")

    return QIcon(icon_path) if os.path.exists(icon_path) else QIcon()


def main():
    # 1. Register Explicit App ID so Windows Taskbar pins the icon properly
    if sys.platform == "win32":
        myappid = "fetchyt.downloader.app.1.0"
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

    app = QApplication(sys.argv)

    # 2. Set App-level Icon (controls taskbar, dock, dialogs)
    app_icon = get_platform_icon()
    app.setWindowIcon(app_icon)

    window = MainWindow()
    # 3. Set Window-level Icon (controls the top-left title bar)
    window.setWindowIcon(app_icon)

    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()