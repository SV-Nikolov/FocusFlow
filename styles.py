"""Shared styling for the FocusFlow PySide6 GUI."""

APP_STYLES = """
QMainWindow, QWidget {
    background-color: #f5f7fb;
    color: #1f2937;
    font-family: Arial, Helvetica, sans-serif;
    font-size: 14px;
}

QLabel#TitleLabel {
    font-size: 26px;
    font-weight: 700;
    color: #111827;
}

QLabel#SectionTitle {
    font-size: 18px;
    font-weight: 700;
    color: #111827;
}

QLabel#CardTitle {
    font-size: 13px;
    font-weight: 700;
    color: #4b5563;
}

QLabel#MetricValue {
    font-size: 28px;
    font-weight: 800;
    color: #2563eb;
}

QFrame#Card {
    background-color: #ffffff;
    border: 1px solid #e5e7eb;
    border-radius: 12px;
    padding: 12px;
}

QLineEdit, QTextEdit, QPlainTextEdit, QComboBox, QDateEdit, QDateTimeEdit {
    background-color: #ffffff;
    border: 1px solid #d1d5db;
    border-radius: 8px;
    padding: 8px;
}

QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus, QComboBox:focus, QDateEdit:focus, QDateTimeEdit:focus {
    border: 1px solid #2563eb;
}

QPushButton {
    background-color: #2563eb;
    color: #ffffff;
    border: none;
    border-radius: 8px;
    padding: 9px 14px;
    font-weight: 700;
}

QPushButton:hover {
    background-color: #1d4ed8;
}

QPushButton#SecondaryButton {
    background-color: #e5e7eb;
    color: #1f2937;
}

QPushButton#SecondaryButton:hover {
    background-color: #d1d5db;
}

QPushButton#DangerButton {
    background-color: #dc2626;
}

QPushButton#DangerButton:hover {
    background-color: #b91c1c;
}

QTabWidget::pane {
    border: 1px solid #e5e7eb;
    border-radius: 10px;
    background: #ffffff;
    padding: 4px;
}

QTabBar::tab {
    background: #e5e7eb;
    color: #1f2937;
    padding: 10px 16px;
    margin-right: 4px;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
}

QTabBar::tab:selected {
    background: #2563eb;
    color: #ffffff;
}

QListWidget, QTableWidget {
    background-color: #ffffff;
    border: 1px solid #e5e7eb;
    border-radius: 10px;
    padding: 6px;
}

QListWidget::item {
    padding: 8px;
    border-bottom: 1px solid #f3f4f6;
}

QListWidget::item:selected {
    background-color: #dbeafe;
    color: #111827;
}
"""
