"""Application entry point for the FocusFlow desktop GUI."""

import sys

from PySide6.QtWidgets import QApplication

from app_window import FocusFlowApp
from styles import APP_STYLES


def main() -> None:
    """Start the FocusFlow PySide6 application."""
    app = QApplication(sys.argv)
    app.setApplicationName("FocusFlow")
    app.setStyleSheet(APP_STYLES)

    window = FocusFlowApp()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
