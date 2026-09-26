"""Transaction details drawer / modal dialog."""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit, QPushButton, QFrame, QGridLayout
)
from PySide6.QtCore import Qt
from app.theme import THEME_COLORS
from core.models import TransactionRecord


class TransactionDetailsDialog(QDialog):
    """Deep-dive forensic dossier for an individual transaction."""

    def __init__(self, record: TransactionRecord, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Transaction Dossier — {record.txid[:16]}...")
        self.resize(750, 550)
        self.setStyleSheet(f"background-color: {THEME_COLORS['bg_dark']}; color: {THEME_COLORS['text_primary']};")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(14)

        # Header Title
        title_box = QVBoxLayout()
        t_lbl = QLabel(f"TRANSACTION FORENSIC RECORD")
        t_lbl.setStyleSheet(f"font-size: 15px; font-weight: 700; color: {THEME_COLORS['accent_blue']};")
        txid_lbl = QLabel(f"TXID: {record.txid}")
        txid_lbl.setStyleSheet(f"font-size: 12px; font-family: monospace; color: {THEME_COLORS['text_secondary']};")
        title_box.addWidget(t_lbl)
        title_box.addWidget(txid_lbl)
        layout.addLayout(title_box)

        # Metadata Grid
        grid_frame = QFrame()
        grid_frame.setStyleSheet(f"background-color: {THEME_COLORS['bg_card']}; border: 1px solid {THEME_COLORS['border']}; border-radius: 6px; padding: 12px;")
        grid = QGridLayout(grid_frame)
        grid.setSpacing(10)

        grid.addWidget(QLabel("Observed Timestamp:"), 0, 0)
        grid.addWidget(QLabel(f"<b>{record.timestamp}</b>"), 0, 1)

        grid.addWidget(QLabel("Source Relay Node:"), 0, 2)
        grid.addWidget(QLabel(f"<b>{record.src_ip}:{record.src_port}</b>"), 0, 3)

        grid.addWidget(QLabel("Destination Node:"), 1, 0)
        grid.addWidget(QLabel(f"<b>{record.dst_ip}:{record.dst_port}</b>"), 1, 1)

        grid.addWidget(QLabel("Country / ASN:"), 1, 2)
        grid.addWidget(QLabel(f"<b>{record.geo_country} • {record.asn}</b>"), 1, 3)

        grid.addWidget(QLabel("Script Type:"), 2, 0)
        grid.addWidget(QLabel(f"<b>{record.script_type}</b>"), 2, 1)

        grid.addWidget(QLabel("Transaction Fee:"), 2, 2)
        grid.addWidget(QLabel(f"<b>{record.fee:.6f} BTC</b>"), 2, 3)

        layout.addWidget(grid_frame)

        # Inputs and Outputs display
        io_box = QHBoxLayout()
        io_box.setSpacing(12)

        # Inputs
        in_box = QVBoxLayout()
        in_lbl = QLabel(f"SPENT INPUTS ({len(record.input_addresses)})")
        in_lbl.setStyleSheet(f"font-size: 11px; font-weight: 700; color: {THEME_COLORS['accent_purple']};")
        in_txt = QTextEdit()
        in_txt.setReadOnly(True)
        in_lines = [
            f"{addr}  ({amt:.4f} BTC)"
            for addr, amt in zip(record.input_addresses, record.input_amounts)
        ]
        in_txt.setText("\n".join(in_lines) if in_lines else "None recorded")
        in_box.addWidget(in_lbl)
        in_box.addWidget(in_txt)
        io_box.addLayout(in_box)

        # Outputs
        out_box = QVBoxLayout()
        out_lbl = QLabel(f"OUTPUT DESTINATIONS ({len(record.output_addresses)})")
        out_lbl.setStyleSheet(f"font-size: 11px; font-weight: 700; color: {THEME_COLORS['accent_amber']};")
        out_txt = QTextEdit()
        out_txt.setReadOnly(True)
        out_lines = [
            f"{addr}  ({amt:.4f} BTC)"
            for addr, amt in zip(record.output_addresses, record.output_amounts)
        ]
        out_txt.setText("\n".join(out_lines) if out_lines else "None recorded")
        out_box.addWidget(out_lbl)
        out_box.addWidget(out_txt)
        io_box.addLayout(out_box)

        layout.addLayout(io_box)

        # Close button
        btn_close = QPushButton("Close")
        btn_close.clicked.connect(self.accept)
        btn_close.setStyleSheet("background-color: #1F2937; border: 1px solid #374151; color: white; padding: 6px 16px; border-radius: 4px;")
        layout.addWidget(btn_close, alignment=Qt.AlignRight)
