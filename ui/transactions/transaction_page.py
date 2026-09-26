"""Transaction Explorer page for forensic querying and deep packet examination."""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QFrame, QScrollArea
)
from PySide6.QtCore import Qt
from app.theme import THEME_COLORS, theme_manager
from core.models import TransactionRecord
from .transaction_details import TransactionDetailsDialog
from ui.components import ForensicComboBox, SearchableComboBox


class TransactionPage(QWidget):
    """Explorer for forensic transactions linking network packets to ledger entries."""

    def __init__(self):
        super().__init__()
        page_layout = QVBoxLayout(self)
        page_layout.setContentsMargins(0, 0, 0, 0)

        # Outer scroll so the whole page scrolls on small screens
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(14)

        # Header Title
        title_box = QVBoxLayout()
        self.title = QLabel("TRANSACTION EXPLORER & LEDGER CORRELATION")
        self.subtitle = QLabel("Search cryptographic TXIDs, inspect P2P broadcast endpoints, and trace multi-input spending.")
        self.subtitle.setWordWrap(True)
        title_box.addWidget(self.title)
        title_box.addWidget(self.subtitle)
        layout.addLayout(title_box)

        # Filter and Search Bar
        self.filter_bar = QFrame()
        fb_layout = QHBoxLayout(self.filter_bar)
        fb_layout.setContentsMargins(8, 6, 8, 6)
        fb_layout.setSpacing(10)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by TXID, IP address, or Bitcoin wallet address...")
        self.search_input.textChanged.connect(self._apply_filters)
        fb_layout.addWidget(self.search_input, 2)

        fb_layout.addWidget(QLabel("Country:"))
        self.country_filter = SearchableComboBox()
        self.country_filter.addItem("All Jurisdictions")
        self.country_filter.currentTextChanged.connect(self._apply_filters)
        fb_layout.addWidget(self.country_filter, 1)

        self.btn_reset_filters = QPushButton("Reset")
        self.btn_reset_filters.setCursor(Qt.PointingHandCursor)
        self.btn_reset_filters.clicked.connect(self._reset_filters)
        fb_layout.addWidget(self.btn_reset_filters)

        layout.addWidget(self.filter_bar)

        # Transaction Table — stretch=1 so it fills available vertical space
        self.tx_table = QTableWidget(0, 8)
        self.tx_table.setHorizontalHeaderLabels([
            "TXID", "Timestamp (UTC)", "Relay IP", "Country", "Inputs", "Outputs", "Volume (BTC)", "Fee (BTC)"
        ])
        self.tx_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tx_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.tx_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tx_table.setMinimumHeight(300)
        self.tx_table.doubleClicked.connect(self._open_tx_details)
        layout.addWidget(self.tx_table, 1)

        scroll.setWidget(content)
        page_layout.addWidget(scroll)

        self.records: list[TransactionRecord] = []
        self.filtered_records: list[TransactionRecord] = []

        self.refresh_theme()
        theme_manager.theme_changed.connect(lambda _: self.refresh_theme())

    def refresh_theme(self):
        """Update element styling according to active theme."""
        self.title.setStyleSheet(f"font-size: 16px; font-weight: 700; color: {THEME_COLORS['text_primary']};")
        self.subtitle.setStyleSheet(f"font-size: 11px; color: {THEME_COLORS['text_secondary']};")
        self.filter_bar.setStyleSheet(f"background-color: {THEME_COLORS['bg_card']}; border: 1px solid {THEME_COLORS['border']}; border-radius: 6px; padding: 6px 12px;")

    def update_data(self, pipeline):
        if not pipeline:
            return
        self.records = pipeline.records

        # Populate unique countries in filter
        countries = sorted(list(set(r.geo_country for r in self.records if r.geo_country and r.geo_country != "Unknown")))
        self.country_filter.blockSignals(True)
        self.country_filter.clear()
        self.country_filter.addItem("All Jurisdictions")
        for c in countries:
            self.country_filter.addItem(c)
        self.country_filter.blockSignals(False)

        self.filtered_records = self.records
        self._populate_table(self.filtered_records)

    def _populate_table(self, records):
        self.tx_table.setRowCount(0)
        for i, r in enumerate(records[:300]):  # Limit initial render for speed
            self.tx_table.insertRow(i)
            item0 = QTableWidgetItem(f"{r.txid[:16]}...")
            item0.setToolTip(f"Full TXID:\n{r.txid}\n\nDouble-click row to open full forensic dossier.")
            self.tx_table.setItem(i, 0, item0)

            self.tx_table.setItem(i, 1, QTableWidgetItem(r.timestamp[:19]))

            item_ip = QTableWidgetItem(r.src_ip)
            item_ip.setToolTip(f"Observed P2P broadcast from {r.src_ip}:{r.src_port}")
            self.tx_table.setItem(i, 2, item_ip)

            self.tx_table.setItem(i, 3, QTableWidgetItem(r.geo_country))
            self.tx_table.setItem(i, 4, QTableWidgetItem(str(len(r.input_addresses))))
            self.tx_table.setItem(i, 5, QTableWidgetItem(str(len(r.output_addresses))))
            self.tx_table.setItem(i, 6, QTableWidgetItem(f"{r.total_output_amount:.4f}"))
            self.tx_table.setItem(i, 7, QTableWidgetItem(f"{r.fee:.6f}"))

    def _apply_filters(self):
        q = self.search_input.text().strip().lower()
        sel_country = self.country_filter.currentText()

        self.filtered_records = [
            r for r in self.records
            if (sel_country == "All Jurisdictions" or r.geo_country == sel_country)
            and (not q or q in r.txid.lower() or q in r.src_ip.lower() or any(q in a.lower() for a in r.input_addresses + r.output_addresses))
        ]
        self._populate_table(self.filtered_records)

    def _reset_filters(self):
        self.search_input.clear()
        self.country_filter.setCurrentIndex(0)
        self.filtered_records = self.records
        self._populate_table(self.filtered_records)

    def _open_tx_details(self, index):
        row = index.row()
        if row < len(self.filtered_records):
            rec = self.filtered_records[row]
            dialog = TransactionDetailsDialog(rec, self)
            dialog.exec()
