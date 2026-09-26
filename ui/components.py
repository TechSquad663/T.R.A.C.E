from PySide6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QWidget,
    QComboBox, QListView, QLineEdit, QListWidget, QListWidgetItem,
    QApplication, QSizePolicy
)
from PySide6.QtCore import Qt, QPoint, QSize, Signal
from PySide6.QtGui import QKeyEvent
from app.theme import THEME_COLORS, theme_manager


class ForensicComboBox(QComboBox):
    """Clean QComboBox with dedicated QListView popup to prevent Windows rendering artifacts."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setView(QListView(self))


# ---------------------------------------------------------------------------
# SearchableComboBox — QComboBox with an integrated inline search field
# Use this for selectors that can have many dynamic items (entities, countries)
# ---------------------------------------------------------------------------

class _SearchPopup(QFrame):
    """
    Floating popup panel containing a search box + filtered list.
    Emits `item_chosen(text, original_index)` when user picks an item.
    Closes itself on Escape or focus-out.
    """
    item_chosen = Signal(str, int)

    def __init__(self, items: list[str], current_index: int, min_width: int, parent=None):
        super().__init__(parent, Qt.Popup | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setObjectName("SearchPopup")
        self._all_items = list(items)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(4)

        # ── Search input ──────────────────────────────────────────────────
        self._search = QLineEdit()
        self._search.setPlaceholderText("🔍  Type to filter...")
        self._search.setClearButtonEnabled(True)
        self._search.setObjectName("SearchPopupInput")
        layout.addWidget(self._search)

        # ── Item list ─────────────────────────────────────────────────────
        self._list = QListWidget()
        self._list.setFrameShape(QFrame.NoFrame)
        self._list.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self._list.setObjectName("SearchPopupList")
        self._populate(items, current_index)
        layout.addWidget(self._list)

        # ── Result count hint ─────────────────────────────────────────────
        self._hint = QLabel()
        self._hint.setAlignment(Qt.AlignRight)
        self._hint.setObjectName("SearchPopupHint")
        layout.addWidget(self._hint)
        self._update_hint()

        # ── Sizing ────────────────────────────────────────────────────────
        row_h = max(self._list.sizeHintForRow(0), 22)
        visible_rows = min(10, max(4, len(items)))
        list_h = row_h * visible_rows + 8
        popup_h = list_h + 70   # search box + hint + margins
        self.setFixedWidth(max(min_width, 320))
        self.setFixedHeight(popup_h)

        # ── Style ─────────────────────────────────────────────────────────
        self._apply_style()
        theme_manager.theme_changed.connect(lambda _: self._apply_style())

        # ── Connections ───────────────────────────────────────────────────
        self._search.textChanged.connect(self._filter)
        self._list.itemActivated.connect(self._on_activated)
        self._list.itemClicked.connect(self._on_activated)

        # Forward arrow keys from the search box into the list
        self._search.installEventFilter(self)

    # ── Public ────────────────────────────────────────────────────────────

    def focus_search(self):
        self._search.setFocus()
        self._search.selectAll()

    # ── Internal ──────────────────────────────────────────────────────────

    def _populate(self, items: list[str], current_index: int):
        self._list.clear()
        for idx, text in enumerate(items):
            item = QListWidgetItem(text)
            item.setData(Qt.UserRole, idx)  # store original index
            self._list.addItem(item)
        if 0 <= current_index < self._list.count():
            self._list.setCurrentRow(current_index)
            self._list.scrollToItem(self._list.currentItem())

    def _filter(self, query: str):
        q = query.strip().lower()
        visible = 0
        for i in range(self._list.count()):
            item = self._list.item(i)
            match = (not q) or (q in item.text().lower())
            item.setHidden(not match)
            if match:
                visible += 1
        # Auto-select first visible
        for i in range(self._list.count()):
            item = self._list.item(i)
            if not item.isHidden():
                self._list.setCurrentItem(item)
                break
        self._update_hint(visible)

    def _update_hint(self, visible: int = None):
        total = len(self._all_items)
        if visible is None:
            visible = total
        if visible == total:
            self._hint.setText(f"{total} items")
        else:
            self._hint.setText(f"{visible} of {total} shown")

    def _on_activated(self, item: QListWidgetItem):
        if item is None or item.isHidden():
            return
        orig_idx = item.data(Qt.UserRole)
        self.item_chosen.emit(item.text(), orig_idx)
        self.close()

    def _apply_style(self):
        bg = THEME_COLORS["bg_card"]
        bg_dark = THEME_COLORS["bg_dark"]
        border = THEME_COLORS["border_light"]
        text = THEME_COLORS["text_primary"]
        text_sec = THEME_COLORS["text_secondary"]
        text_muted = THEME_COLORS["text_muted"]
        accent = THEME_COLORS["accent_blue"]
        sel_bg = THEME_COLORS["bg_card_alt"]

        self.setStyleSheet(f"""
            QFrame#SearchPopup {{
                background-color: {bg};
                border: 1px solid {border};
                border-radius: 8px;
            }}

            QLineEdit#SearchPopupInput {{
                background-color: {bg_dark};
                border: 1px solid {border};
                border-radius: 6px;
                padding: 6px 10px;
                color: {text};
                font-size: 12px;
            }}
            QLineEdit#SearchPopupInput:focus {{
                border-color: {accent};
            }}

            QListWidget#SearchPopupList {{
                background-color: {bg};
                border: none;
                color: {text};
                font-size: 12px;
                outline: none;
            }}
            QListWidget#SearchPopupList::item {{
                padding: 5px 10px;
                border-radius: 4px;
                min-height: 22px;
            }}
            QListWidget#SearchPopupList::item:hover {{
                background-color: {sel_bg};
                color: {text};
            }}
            QListWidget#SearchPopupList::item:selected {{
                background-color: {sel_bg};
                color: {accent};
                font-weight: 600;
            }}

            QLabel#SearchPopupHint {{
                color: {text_muted};
                font-size: 10px;
                padding: 0 4px;
            }}

            QScrollBar:vertical {{
                border: none;
                background: {bg_dark};
                width: 6px;
                margin: 0;
            }}
            QScrollBar::handle:vertical {{
                background: {border};
                min-height: 16px;
                border-radius: 3px;
            }}
        """)

    # ── Event filter: forward key events from search -> list ──────────────

    def eventFilter(self, obj, event):
        if obj is self._search and isinstance(event, QKeyEvent):
            key = event.key()
            if key == Qt.Key_Down:
                self._move_selection(1)
                return True
            elif key == Qt.Key_Up:
                self._move_selection(-1)
                return True
            elif key in (Qt.Key_Return, Qt.Key_Enter):
                item = self._list.currentItem()
                if item and not item.isHidden():
                    self._on_activated(item)
                return True
            elif key == Qt.Key_Escape:
                self.close()
                return True
        return super().eventFilter(obj, event)

    def _move_selection(self, delta: int):
        count = self._list.count()
        row = self._list.currentRow()
        # Find next visible item in direction
        step = 1 if delta > 0 else -1
        r = row + step
        while 0 <= r < count:
            if not self._list.item(r).isHidden():
                self._list.setCurrentRow(r)
                self._list.scrollToItem(self._list.currentItem())
                return
            r += step


class SearchableComboBox(QComboBox):
    """
    A QComboBox that opens a custom searchable popup instead of the native dropdown.

    Drop-in replacement for ForensicComboBox on selectors with many items (entities,
    countries, etc.). For small static lists (< 8 items), ForensicComboBox is fine.

    The standard `currentIndexChanged`, `currentTextChanged`, and `addItem` / `clear`
    API all work identically to a regular QComboBox.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        # Hide native popup; we replace it entirely
        self.setView(QListView(self))
        self._popup_open = False
        self._apply_style()
        theme_manager.theme_changed.connect(lambda _: self._apply_style())

    def showPopup(self):
        """Override: show our custom searchable popup instead of native dropdown."""
        if self._popup_open:
            return
        self._popup_open = True

        items = [self.itemText(i) for i in range(self.count())]
        if not items:
            self._popup_open = False
            return

        popup = _SearchPopup(
            items=items,
            current_index=self.currentIndex(),
            min_width=self.width(),
            parent=self.window(),
        )

        # Position popup just below the combo box
        global_pos: QPoint = self.mapToGlobal(QPoint(0, self.height()))
        popup.move(global_pos)

        popup.item_chosen.connect(self._on_item_chosen)
        popup.destroyed.connect(self._on_popup_closed)

        popup.show()
        popup.raise_()
        popup.focus_search()

    def hidePopup(self):
        """No-op; our popup closes itself."""
        pass

    def _on_item_chosen(self, text: str, orig_idx: int):
        self.setCurrentIndex(orig_idx)

    def _on_popup_closed(self):
        self._popup_open = False

    def _apply_style(self):
        """Style the combo button itself to match ForensicComboBox."""
        bg = THEME_COLORS["bg_card"]
        border = THEME_COLORS["border_light"]
        text = THEME_COLORS["text_primary"]
        text_sec = THEME_COLORS["text_secondary"]
        accent = THEME_COLORS["accent_blue"]
        self.setStyleSheet(f"""
            QComboBox {{
                background-color: {bg};
                border: 1px solid {border};
                border-radius: 6px;
                padding: 6px 30px 6px 10px;
                color: {text};
                min-height: 22px;
            }}
            QComboBox:hover {{
                border-color: {accent};
            }}
            QComboBox::drop-down {{
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 24px;
                border-left: none;
            }}
            QComboBox::down-arrow {{
                width: 0;
                height: 0;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 5px solid {text_sec};
            }}
        """)


# ---------------------------------------------------------------------------
# KPICard, RiskBadge, EmptyStateWidget (unchanged)
# ---------------------------------------------------------------------------

class KPICard(QFrame):
    """Forensic metric KPI card."""

    def __init__(self, title: str, value: str = "0", subtext: str = "", accent_color: str = "#38BDF8"):
        super().__init__()
        self.setObjectName("KPICard")
        self.title_text = title
        self.subtext = subtext
        self.accent_color = accent_color

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(4)

        self.title_lbl = QLabel(title.upper())
        self.val_lbl = QLabel(value)
        self.sub_lbl = QLabel(subtext)

        layout.addWidget(self.title_lbl)
        layout.addWidget(self.val_lbl)
        layout.addWidget(self.sub_lbl)

        self.refresh_theme()
        theme_manager.theme_changed.connect(lambda _: self.refresh_theme())

    def refresh_theme(self):
        """Reapply dynamic colors based on active theme."""
        self.setStyleSheet(f"""
            QFrame#KPICard {{
                background-color: {THEME_COLORS['bg_card']};
                border: 1px solid {THEME_COLORS['border']};
                border-top: 3px solid {self.accent_color};
                border-radius: 8px;
                padding: 12px;
            }}
            QFrame#KPICard:hover {{
                border-color: {THEME_COLORS['border_light']};
            }}
        """)
        self.title_lbl.setStyleSheet(f"color: {THEME_COLORS['text_muted']}; font-size: 10px; font-weight: 700; letter-spacing: 0.5px;")
        self.val_lbl.setStyleSheet(f"color: {THEME_COLORS['text_primary']}; font-size: 22px; font-weight: 700;")
        self.sub_lbl.setStyleSheet(f"color: {THEME_COLORS['text_secondary']}; font-size: 11px;")

    def set_value(self, val: str, subtext: str = ""):
        self.val_lbl.setText(val)
        if subtext:
            self.sub_lbl.setText(subtext)


class RiskBadge(QLabel):
    """Semantic priority and risk indicator badge."""

    def __init__(self, text: str, level: str = "Low"):
        super().__init__(text)
        self.setAlignment(Qt.AlignCenter)
        self.level = level
        self.set_level(level)
        theme_manager.theme_changed.connect(lambda _: self.set_level(self.level))

    def set_level(self, level: str):
        self.level = level
        colors_map = {
            "Critical": (THEME_COLORS["accent_red"], "rgba(239, 68, 68, 0.15)"),
            "High": (THEME_COLORS["accent_orange"], "rgba(249, 115, 22, 0.15)"),
            "Medium": (THEME_COLORS["accent_amber"], "rgba(245, 158, 11, 0.15)"),
            "Low": (THEME_COLORS["accent_emerald"], "rgba(16, 185, 129, 0.15)"),
            "Informational": (THEME_COLORS["accent_blue"], "rgba(56, 189, 248, 0.15)"),
        }
        fg, bg = colors_map.get(level, (THEME_COLORS["text_secondary"], THEME_COLORS["border"]))
        self.setStyleSheet(f"""
            QLabel {{
                color: {fg};
                background-color: {bg};
                border: 1px solid {fg};
                border-radius: 4px;
                padding: 3px 8px;
                font-weight: 700;
                font-size: 11px;
            }}
        """)


class EmptyStateWidget(QFrame):
    """Clean empty state displayed when no dataset is loaded."""

    def __init__(self, on_generate_demo=None, on_import_dataset=None):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(16)

        icon_lbl = QLabel("🛡️")
        icon_lbl.setStyleSheet("font-size: 48px;")
        icon_lbl.setAlignment(Qt.AlignCenter)

        self.title_lbl = QLabel("No Dataset Loaded")
        self.title_lbl.setAlignment(Qt.AlignCenter)

        self.desc_lbl = QLabel(
            "TRACE operates 100% offline on bulk Bitcoin transaction and P2P network metadata.\n"
            "Generate a synthetic demo dataset or import a local CSV, JSON, or XML file to begin analysis."
        )
        self.desc_lbl.setAlignment(Qt.AlignCenter)

        btn_box = QHBoxLayout()
        btn_box.setSpacing(12)
        btn_box.setAlignment(Qt.AlignCenter)

        self.btn_demo = QPushButton("🚀 Generate Demo Dataset & Analyze")
        self.btn_demo.setObjectName("btn_demo")
        self.btn_demo.setProperty("class", "btn-primary")
        if on_generate_demo:
            self.btn_demo.clicked.connect(on_generate_demo)

        self.btn_import = QPushButton("📂 Import Local File (CSV / JSON / XML)")
        self.btn_import.setProperty("class", "btn-secondary")
        if on_import_dataset:
            self.btn_import.clicked.connect(on_import_dataset)

        btn_box.addWidget(self.btn_demo)
        btn_box.addWidget(self.btn_import)

        layout.addWidget(icon_lbl)
        layout.addWidget(self.title_lbl)
        layout.addWidget(self.desc_lbl)
        layout.addLayout(btn_box)

        self.refresh_theme()
        theme_manager.theme_changed.connect(lambda _: self.refresh_theme())

    def refresh_theme(self):
        """Update text and button styles according to current theme."""
        self.title_lbl.setStyleSheet(f"color: {THEME_COLORS['text_primary']}; font-size: 18px; font-weight: 700;")
        self.desc_lbl.setStyleSheet(f"color: {THEME_COLORS['text_secondary']}; font-size: 13px; text-align: center;")
        self.btn_demo.setStyleSheet(f"""
            QPushButton {{
                background-color: {THEME_COLORS['accent_blue']};
                color: #FFFFFF;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-weight: 700;
                font-size: 13px;
            }}
            QPushButton:hover {{ background-color: #1D4ED8; }}
        """)
        self.btn_import.setStyleSheet(f"""
            QPushButton {{
                background-color: {THEME_COLORS['bg_card']};
                color: {THEME_COLORS['text_primary']};
                border: 1px solid {THEME_COLORS['border_light']};
                border-radius: 6px;
                padding: 10px 18px;
                font-weight: 600;
                font-size: 13px;
            }}
            QPushButton:hover {{ background-color: {THEME_COLORS['bg_card_alt']}; border-color: {THEME_COLORS['accent_blue']}; }}
        """)
