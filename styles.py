"""Styling file for the QT widgets
"""
THEME = """
QWidget {
    background-color: #0f172a;
    color: #f8fafc;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    font-size: 13px;
}

QLineEdit, QComboBox, QTextEdit {
    background-color: #1e293b;
    border: 1px solid #334155;
    border-radius: 8px;
    padding: 8px 12px;
    color: #f8fafc;
    selection-background-color: #3b82f6;
    selection-color: #ffffff;
}

QLineEdit:focus, QComboBox:focus, QTextEdit:focus {
    border: 1.5px solid #3b82f6;
    background-color: #0f172a;
}

/* Dropdown Arrow Fix */
QComboBox {
    padding-right: 30px;
}

QComboBox::drop-down {
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 25px;
    border-left-width: 0px;
}

QComboBox::down-arrow {
    image: none;
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-top: 5px solid #94a3b8;
    margin-right: 8px;
}

QComboBox::down-arrow:hover {
    border-top: 5px solid #f8fafc;
}

QComboBox QAbstractItemView {
    background-color: #1e293b;
    border: 1px solid #334155;
    border-radius: 8px;
    color: #f8fafc;
    selection-background-color: #3b82f6;
    selection-color: #ffffff;
    padding: 4px;
}

/* Buttons */
QPushButton {
    background-color: #2563eb;
    color: #ffffff;
    border-radius: 8px;
    padding: 9px 18px;
    font-weight: 600;
    border: none;
}

QPushButton:hover {
    background-color: #1d4ed8;
}

QPushButton:pressed {
    background-color: #1e40af;
}

QPushButton:disabled {
    background-color: #334155;
    color: #64748b;
}

/* Secondary Buttons */
QPushButton#browseBtn, QPushButton#logToggleBtn, QPushButton#aboutBtn {
    background-color: #1e293b;
    border: 1px solid #334155;
    color: #cbd5e1;
    font-weight: 500;
}

QPushButton#browseBtn:hover, QPushButton#logToggleBtn:hover, QPushButton#aboutBtn:hover {
    background-color: #334155;
    color: #ffffff;
    border-color: #475569;
}

QPushButton#browseBtn:pressed, QPushButton#logToggleBtn:pressed, QPushButton#aboutBtn:pressed {
    background-color: #0f172a;
}

QMessageBox {
    background-color: #0f172a;
}

QMessageBox QLabel {
    color: #f8fafc;
}

QMessageBox QPushButton {
    background-color: #2563eb;
    min-width: 70px;
}

/* Preview Card */
QFrame#previewCard {
    background-color: #1e293b;
    border: 1px solid #334155;
    border-radius: 8px;
    padding: 10px;
}

/* Progress Bar */
QProgressBar {
    background-color: #1e293b;
    border: 1px solid #334155;
    border-radius: 8px;
    text-align: center;
    color: #f8fafc;
    font-size: 11px;
    font-weight: 600;
    height: 16px;
}

QProgressBar::chunk {
    background-color: #3b82f6;
    border-radius: 6px;
}
"""