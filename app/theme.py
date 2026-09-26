"""Dark cybersecurity workstation theme and Qt Stylesheets (QSS) for TRACE."""

THEME_COLORS = {
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

DARK_STYLESHEET = """
QMainWindow {
    background-color: #0B0F19;
    color: #F8FAFC;
    font-family: 'Segoe UI', 'SF Pro Text', 'Ubuntu', 'Helvetica Neue', sans-serif;
    font-size: 13px;
}

QWidget {
    background-color: #0B0F19;
    color: #F8FAFC;
    selection-background-color: #2563EB;
    selection-color: #FFFFFF;
}

/* Sidebar Styling */
QFrame#SidebarFrame {
    background-color: #080C14;
    border-right: 1px solid #1F2937;
    min-width: 230px;
    max-width: 230px;
}

QPushButton.nav-btn {
    text-align: left;
    padding: 10px 16px;
    border-radius: 6px;
    border: none;
    background-color: transparent;
    color: #94A3B8;
    font-size: 13px;
    font-weight: 500;
}

QPushButton.nav-btn:hover {
    background-color: #111827;
    color: #F8FAFC;
}

QPushButton.nav-btn:checked {
    background-color: #1E293B;
    color: #38BDF8;
    font-weight: 600;
    border-left: 3px solid #38BDF8;
}

/* Header & Status Bar */
QFrame#HeaderFrame {
    background-color: #080C14;
    border-bottom: 1px solid #1F2937;
    min-height: 52px;
    max-height: 52px;
    padding: 0px 16px;
}

QStatusBar {
    background-color: #080C14;
    border-top: 1px solid #1F2937;
    color: #64748B;
    font-size: 11px;
}

/* Content Area & Cards */
QFrame.kpi-card {
    background-color: #111827;
    border: 1px solid #1F2937;
    border-radius: 8px;
    padding: 14px;
}

QFrame.kpi-card:hover {
    border-color: #374151;
}

QFrame.evidence-card {
    background-color: #111827;
    border: 1px solid #1F2937;
    border-radius: 8px;
    padding: 16px;
}

/* Standard Buttons */
QPushButton.btn-primary {
    background-color: #2563EB;
    color: #FFFFFF;
    border: none;
    border-radius: 6px;
    padding: 8px 18px;
    font-weight: 600;
    font-size: 12px;
}

QPushButton.btn-primary:hover {
    background-color: #1D4ED8;
}

QPushButton.btn-success {
    background-color: #059669;
    color: #FFFFFF;
    border: none;
    border-radius: 6px;
    padding: 8px 18px;
    font-weight: 600;
    font-size: 12px;
}

QPushButton.btn-success:hover {
    background-color: #047857;
}

QPushButton.btn-secondary {
    background-color: #1F2937;
    color: #E2E8F0;
    border: 1px solid #374151;
    border-radius: 6px;
    padding: 8px 16px;
    font-weight: 500;
    font-size: 12px;
}

QPushButton.btn-secondary:hover {
    background-color: #374151;
}

/* Tables */
QTableWidget {
    background-color: #111827;
    border: 1px solid #1F2937;
    border-radius: 6px;
    gridline-color: #1F2937;
    color: #F8FAFC;
}

QHeaderView::section {
    background-color: #080C14;
    color: #94A3B8;
    padding: 8px;
    border: none;
    border-bottom: 1px solid #1F2937;
    font-weight: 600;
    font-size: 11px;
    text-transform: uppercase;
}

QTableWidget::item {
    padding: 6px;
    border-bottom: 1px solid #111827;
}

QTableWidget::item:selected {
    background-color: #1E293B;
    color: #38BDF8;
}

/* Inputs & Search */
QLineEdit {
    background-color: #111827;
    border: 1px solid #374151;
    border-radius: 6px;
    padding: 7px 12px;
    color: #F8FAFC;
}

QLineEdit:focus {
    border-color: #38BDF8;
}

/* ScrollBars */
QScrollBar:vertical {
    border: none;
    background: #0B0F19;
    width: 8px;
    margin: 0px;
}

QScrollBar::handle:vertical {
    background: #374151;
    min-height: 20px;
    border-radius: 4px;
}

QScrollBar::handle:vertical:hover {
    background: #4B5563;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

/* TabWidget */
QTabWidget::pane {
    border: 1px solid #1F2937;
    background: #111827;
    border-radius: 6px;
}

QTabBar::tab {
    background: #080C14;
    color: #94A3B8;
    padding: 8px 16px;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    margin-right: 2px;
}

QTabBar::tab:selected {
    background: #111827;
    color: #38BDF8;
    font-weight: 600;
}
"""
