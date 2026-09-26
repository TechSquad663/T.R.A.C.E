"""Transaction Explorer page for forensic querying and deep packet examination."""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QFrame
)
from PySide6.QtCore import Qt
from app.theme import THEME_COLORS
from core.models import TransactionRecord
from .transaction_details import TransactionDetailsDialog


class TransactionPage(QWidget):
    """Explorer for forensic transactions linking network packets to ledger entries."""

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(14)

        # Header Title
        title_box = QVBoxLayout()
        title = QLabel("TRANSACTION EXPLORER & LEDGER CORRELATION")
        title.setStyleSheet(f"font-size: 16px; font-weight: 700; color: {THEME_COLORS['text_primary']};")
        subtitle = QLabel("Search cryptographic TXIDs, inspect P2P broadcast endpoints, and trace multi-input spending.")
        subtitle.setStyleSheet(f"font-size: 11px; color: {THEME_COLORS['text_secondary']};")
        title_box.addWidget(title)
        title_box.addWidget(subtitle)
        layout.addLayout(title_box)

        # Search Bar
        search_box = QHBoxLayout()
        search_box.setSpacing(10)
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by 64-hex TXID, IP address, or Bitcoin wallet...")
        self.search_input.textChanged.connect(self._filter_transactions)
        search_box.addWidget(self.search_input)

        layout.addLayout(search_box)

        # Transaction Table
        self.tx_table = QTableWidget(0, 8)
        self.tx_table.setHorizontalHeaderLabels([
            "TXID", "Timestamp (UTC)", "Relay IP", "Country", "Inputs", "Outputs", "Volume (BTC)", "Fee (BTC)"
        ])
        self.tx_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tx_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.tx_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tx_table.doubleClicked.connect(self._open_tx_details)
        layout.addWidget(self.tx_table)

        self.records: list[TransactionRecord] = []

    def update_data(self, pipeline):
        if not pipeline:
            return
        self.records = pipeline.records
        self._populate_table(self.records)

    def _populate_table(self, records):
        self.tx_table.setRowCount(0)
        for i, r in enumerate(records[:300]):  # Limit initial render for speed
            self.tx_table.insertRow(i)
            self.tx_table.setItem(i, 0, QTableWidgetItem(f"{r.txid[:16]}..."))
            self.tx_table.setItem(i, 1, QTableWidgetItem(r.timestamp[:19]))
            self.tx_table.setItem(i, 2, QTableWidgetItem(r.src_ip))
            self.tx_table.setItem(i, 3, QTableWidgetItem(r.geo_country))
            self.tx_table.setItem(i, 4, QTableWidgetItem(str(len(r.input_addresses))))
            self.tx_table.setItem(i, 5, QTableWidgetItem(str(len(r.output_addresses))))
            self.tx_table.setItem(i, 6, QTableWidgetItem(f"{r.total_output_amount:.4f}"))
            self.tx_table.setItem(i, 7, QTableWidgetItem(f"{r.fee:.6f}"))

    def _filter_transactions(self, query: str):
        q = query.strip().lower()
        if not q:
            self._populate_table(self.records)
            return

        filtered = [
            r for r in self.records
            if q in r.txid.lower() or q in r.src_ip.lower() or any(q in a.lower() for a in r.input_addresses + r.output_addresses)
        ]
        self._populate_table(filtered)

    def _open_tx_details(self, index):
        row = index.row()
        if row < len(self.records):
            rec = self.records[row]
            dialog = TransactionDetailsDialog(rec, self)
            dialog.exec()
