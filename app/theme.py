"""Dark cybersecurity workstation and Light analyst themes with Qt Stylesheets (QSS) for TRACE."""
from PySide6.QtCore import QObject, Signal

DARK_THEME_COLORS = {
    "bg_dark": "#0B0F19",       # Deep Obsidian
    "bg_card": "#111827",       # Charcoal Slate
    "bg_card_alt": "#1E293B",   # Medium Slate
    "border": "#1F2937",        # Dark Border
    "border_light": "#374151",  # Visible Border
    "text_primary": "#F8FAFC",  # Near White
    "text_secondary": "#94A3B8",# Slate Muted
    "text_muted": "#64748B",    # Muted Gray
    "accent_blue": "#38BDF8",   # Sky Blue / Info
    "accent_purple": "#A855F7", # Purple / Wallet
    "accent_amber": "#F59E0B",  # Amber / Elevated
    "accent_orange": "#F97316", # Orange / High Risk
    "accent_red": "#EF4444",    # Crimson / Critical
    "accent_emerald": "#10B981",# Emerald / Normal / Low Risk
    "accent_cyan": "#06B6D4",   # Cyan / Cluster
}

LIGHT_THEME_COLORS = {
    "bg_dark": "#F1F5F9",       # Crisp Light Slate Background
    "bg_card": "#FFFFFF",       # Pure White Card
    "bg_card_alt": "#F8FAFC",   # Highlight Card Slate
    "border": "#E2E8F0",        # Clean Light Border
    "border_light": "#CBD5E1",  # Visible Border Slate
    "text_primary": "#0F172A",  # Deep Slate (High Contrast Readability)
    "text_secondary": "#475569",# Medium Slate
    "text_muted": "#64748B",    # Muted Slate Gray
    "accent_blue": "#0284C7",   # Royal Sky Blue
    "accent_purple": "#7C3AED", # Deep Violet
    "accent_amber": "#D97706",  # Warm Amber Gold
    "accent_orange": "#EA580C", # High-Risk Orange
    "accent_red": "#DC2626",    # Crimson Critical
    "accent_emerald": "#059669",# Deep Forest Emerald
    "accent_cyan": "#0891B2",   # Rich Cyan
}

# Active theme color dictionary, mutated in-place when theme changes
THEME_COLORS = dict(DARK_THEME_COLORS)


def get_theme_colors(theme_name: str = "dark") -> dict:
    """Return dictionary of theme colors for given theme name."""
    if theme_name.lower() == "light":
        return LIGHT_THEME_COLORS
    return DARK_THEME_COLORS


def get_stylesheet(theme_name: str = "dark") -> str:
    """Generate complete Qt Stylesheet (QSS) for dark or light theme."""
    is_dark = (theme_name.lower() != "light")
    c = DARK_THEME_COLORS if is_dark else LIGHT_THEME_COLORS
    
    sidebar_bg = "#080C14" if is_dark else "#FFFFFF"
    header_bg = "#080C14" if is_dark else "#FFFFFF"
    status_bg = "#080C14" if is_dark else "#FFFFFF"
    table_header_bg = "#080C14" if is_dark else "#F8FAFC"
    nav_btn_color = "#94A3B8" if is_dark else "#475569"
    nav_btn_hover_bg = "#111827" if is_dark else "#F1F5F9"
    nav_btn_hover_fg = "#F8FAFC" if is_dark else "#0F172A"
    nav_btn_checked_bg = "#1E293B" if is_dark else "#E0F2FE"
    btn_sec_bg = "#1F2937" if is_dark else "#FFFFFF"
    btn_sec_hover = "#374151" if is_dark else "#F1F5F9"
    btn_primary_hover = "#1D4ED8" if is_dark else "#0369A1"
    sel_bg = "#1E293B" if is_dark else "#E0F2FE"
    tab_unselected_bg = "#080C14" if is_dark else "#F1F5F9"
    progress_bg = "#1E293B" if is_dark else "#E2E8F0"
    tooltip_bg = "#1E293B" if is_dark else "#FFFFFF"

    return f"""
QMainWindow {{
    background-color: {c['bg_dark']};
    color: {c['text_primary']};
    font-family: 'Segoe UI', 'Inter', -apple-system, sans-serif;
    font-size: 13px;
}}

QWidget {{
    background-color: {c['bg_dark']};
    color: {c['text_primary']};
    selection-background-color: {c['accent_blue']};
    selection-color: #FFFFFF;
}}

/* Sidebar Styling */
QFrame#SidebarFrame {{
    background-color: {sidebar_bg};
    border-right: 1px solid {c['border']};
    min-width: 230px;
    max-width: 230px;
}}

QPushButton.nav-btn {{
    text-align: left;
    padding: 10px 16px;
    border-radius: 6px;
    border: none;
    background-color: transparent;
    color: {nav_btn_color};
    font-size: 13px;
    font-weight: 500;
}}

QPushButton.nav-btn:hover {{
    background-color: {nav_btn_hover_bg};
    color: {nav_btn_hover_fg};
}}

QPushButton.nav-btn:checked {{
    background-color: {nav_btn_checked_bg};
    color: {c['accent_blue']};
    font-weight: 600;
    border-left: 3px solid {c['accent_blue']};
}}

/* Header & Status Bar */
QFrame#HeaderFrame {{
    background-color: {header_bg};
    border-bottom: 1px solid {c['border']};
    min-height: 52px;
    max-height: 52px;
    padding: 0px 16px;
}}

QStatusBar {{
    background-color: {status_bg};
    border-top: 1px solid {c['border']};
    color: {c['text_muted']};
    font-size: 11px;
}}

/* Forensic Cards & Frames */
QFrame.kpi-card, QFrame.evidence-card, QFrame.forensic-card, QFrame.card {{
    background-color: {c['bg_card']};
    border: 1px solid {c['border']};
    border-radius: 8px;
    padding: 14px;
}}

QFrame.kpi-card:hover, QFrame.evidence-card:hover, QFrame.forensic-card:hover, QFrame.card:hover {{
    border-color: {c['border_light']};
}}

/* Standard Buttons */
QPushButton.btn-primary {{
    background-color: {c['accent_blue']};
    color: #FFFFFF;
    border: none;
    border-radius: 6px;
    padding: 8px 18px;
    font-weight: 600;
    font-size: 12px;
}}

QPushButton.btn-primary:hover {{
    background-color: {btn_primary_hover};
}}

QPushButton.btn-success {{
    background-color: #059669;
    color: #FFFFFF;
    border: none;
    border-radius: 6px;
    padding: 8px 18px;
    font-weight: 600;
    font-size: 12px;
}}

QPushButton.btn-success:hover {{
    background-color: #047857;
}}

QPushButton.btn-secondary {{
    background-color: {btn_sec_bg};
    color: {c['text_primary']};
    border: 1px solid {c['border_light']};
    border-radius: 6px;
    padding: 8px 16px;
    font-weight: 500;
    font-size: 12px;
}}

QPushButton.btn-secondary:hover {{
    background-color: {btn_sec_hover};
    border-color: {c['accent_blue']};
}}

QPushButton {{
    background-color: {btn_sec_bg};
    color: {c['text_primary']};
    border: 1px solid {c['border_light']};
    border-radius: 6px;
    padding: 6px 14px;
    font-weight: 500;
    font-size: 12px;
}}

QPushButton:hover {{
    background-color: {btn_sec_hover};
}}

/* Tables */
QTableWidget {{
    background-color: {c['bg_card']};
    border: 1px solid {c['border']};
    border-radius: 6px;
    gridline-color: {c['border']};
    color: {c['text_primary']};
}}

QHeaderView::section {{
    background-color: {table_header_bg};
    color: {c['text_secondary']};
    padding: 8px;
    border: none;
    border-bottom: 1px solid {c['border']};
    font-weight: 600;
    font-size: 11px;
    text-transform: uppercase;
}}

QTableWidget::item {{
    padding: 6px;
    border-bottom: 1px solid {c['border']};
}}

QTableWidget::item:selected {{
    background-color: {sel_bg};
    color: {c['accent_blue']};
}}

/* Inputs, TextAreas & Spinboxes */
QLineEdit, QTextEdit, QDoubleSpinBox, QSpinBox {{
    background-color: {c['bg_card']};
    border: 1px solid {c['border_light']};
    border-radius: 6px;
    padding: 7px 12px;
    color: {c['text_primary']};
}}

QLineEdit:focus, QTextEdit:focus, QDoubleSpinBox:focus, QSpinBox:focus {{
    border-color: {c['accent_blue']};
}}

QComboBox {{
    background-color: {c['bg_card']};
    border: 1px solid {c['border_light']};
    border-radius: 6px;
    padding: 6px 12px;
    color: {c['text_primary']};
    min-height: 20px;
}}

QComboBox:focus {{
    border-color: {c['accent_blue']};
}}

QComboBox QAbstractItemView {{
    background-color: {c['bg_card']};
    color: {c['text_primary']};
    border: 1px solid {c['border_light']};
    selection-background-color: {sel_bg};
    selection-color: {c['accent_blue']};
}}

/* ScrollBars */
QScrollBar:vertical {{
    border: none;
    background: {c['bg_dark']};
    width: 8px;
    margin: 0px;
}}

QScrollBar::handle:vertical {{
    background: {c['border_light']};
    min-height: 20px;
    border-radius: 4px;
}}

QScrollBar::handle:vertical:hover {{
    background: {c['text_muted']};
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0px;
}}

QScrollBar:horizontal {{
    border: none;
    background: {c['bg_dark']};
    height: 8px;
    margin: 0px;
}}

QScrollBar::handle:horizontal {{
    background: {c['border_light']};
    min-width: 20px;
    border-radius: 4px;
}}

QScrollBar::handle:horizontal:hover {{
    background: {c['text_muted']};
}}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
    width: 0px;
}}

/* TabWidget */
QTabWidget::pane {{
    border: 1px solid {c['border']};
    background: {c['bg_card']};
    border-radius: 6px;
}}

QTabBar::tab {{
    background: {tab_unselected_bg};
    color: {c['text_secondary']};
    padding: 8px 16px;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    margin-right: 2px;
}}

QTabBar::tab:selected {{
    background: {c['bg_card']};
    color: {c['accent_blue']};
    font-weight: 600;
}}

/* Progress Bar */
QProgressBar {{
    background: {progress_bg};
    border: 1px solid {c['border']};
    border-radius: 4px;
    text-align: center;
    color: {c['text_primary']};
}}

QProgressBar::chunk {{
    background-color: {c['accent_blue']};
    border-radius: 3px;
}}

/* ToolTip & Dialogs */
QToolTip {{
    background-color: {tooltip_bg};
    color: {c['text_primary']};
    border: 1px solid {c['border_light']};
    border-radius: 4px;
    padding: 4px 8px;
    font-size: 11px;
}}

QDialog, QMessageBox, QProgressDialog {{
    background-color: {c['bg_dark']};
    color: {c['text_primary']};
}}
"""


DARK_STYLESHEET = get_stylesheet("dark")
LIGHT_STYLESHEET = get_stylesheet("light")


class ThemeManager(QObject):
    """Manages application visual theme switching between Dark and Light modes."""

    theme_changed = Signal(str)  # Emits theme name ("dark" or "light")
    _instance = None

    def __init__(self):
        super().__init__()
        self.current_theme = "dark"

    @classmethod
    def get_instance(cls) -> "ThemeManager":
        """Get or initialize singleton instance of ThemeManager."""
        if cls._instance is None:
            cls._instance = ThemeManager()
        return cls._instance

    def set_theme(self, theme_name: str):
        """Switch active theme and update application stylesheet and palette."""
        theme_name = theme_name.lower().strip()
        if theme_name not in ("dark", "light"):
            theme_name = "dark"
        if theme_name == self.current_theme:
            return
        self.current_theme = theme_name
        palette = DARK_THEME_COLORS if theme_name == "dark" else LIGHT_THEME_COLORS
        THEME_COLORS.update(palette)

        from PySide6.QtWidgets import QApplication
        app = QApplication.instance()
        if app:
            app.setStyleSheet(get_stylesheet(theme_name))

        self.theme_changed.emit(theme_name)

    def toggle_theme(self):
        """Toggle between Dark and Light mode."""
        new_theme = "light" if self.current_theme == "dark" else "dark"
        self.set_theme(new_theme)

    def is_dark(self) -> bool:
        """Return True if currently in dark mode."""
        return self.current_theme == "dark"


# Global singleton instance
theme_manager = ThemeManager.get_instance()
