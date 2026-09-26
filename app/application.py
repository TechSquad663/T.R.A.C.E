"""TRACE Application bootstrap and runtime manager."""
import sys
import logging
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from config.settings import get_settings
from config.logging_config import setup_logging
from .theme import DARK_STYLESHEET, theme_manager, get_stylesheet

logger = logging.getLogger("TRACE.App")


class TRACEApplication:
    """Manages application lifecycle and Qt context."""

    def __init__(self, sys_argv=None):
        self.settings = get_settings()
        setup_logging()

        # High DPI attributes
        if hasattr(Qt, "AA_EnableHighDpiScaling"):
            QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
        if hasattr(Qt, "AA_UseHighDpiPixmaps"):
            QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

        self.app = QApplication(sys_argv or sys.argv)
        self.app.setApplicationName(self.settings.APP_NAME)
        self.app.setApplicationVersion(self.settings.VERSION)
        self.app.setOrganizationName("NTRO")
        
        initial_theme = getattr(self.settings, "THEME", "dark")
        self.app.setStyleSheet(get_stylesheet(initial_theme))
        theme_manager.current_theme = initial_theme

    def exec(self):
        return self.app.exec()
