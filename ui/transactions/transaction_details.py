"""Transaction details drawer / modal dialog with responsive scroll layout and forensic copy actions."""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit, QPushButton,
    QFrame, QGridLayout, QScrollArea, QWidget, QApplication
)
from PySide6.QtCore import Qt, QTimer
from app.theme import THEME_COLORS, theme_manager
from core.models import TransactionRecord


class TransactionDetailsDialog(QDialog):
    """Deep-dive forensic dossier for an individual transaction."""

    def __init__(self, record: TransactionRecord, parent=None):
        super().__init__(parent)
        self.record = record
        self.setWindowTitle(f"Transaction Dossier — {record.txid[:16]}...")
        self.resize(780, 580)
        self.setMinimumSize(600, 420)
        self.setStyleSheet(f"background-color: {THEME_COLORS['bg_dark']}; color: {THEME_COLORS['text_primary']};")

        dialog_layout = QVBoxLayout(self)
        dialog_layout.setContentsMargins(16, 16, 16, 16)
        dialog_layout.setSpacing(12)

        # Header Title with Copy TXID Action
        header_frame = QFrame()
        h_layout = QHBoxLayout(header_frame)
        h_layout.setContentsMargins(0, 0, 0, 0)
        h_layout.setSpacing(12)

        title_box = QVBoxLayout()
        t_lbl = QLabel("TRANSACTION FORENSIC RECORD")
        t_lbl.setStyleSheet(f"font-size: 15px; font-weight: 700; color: {THEME_COLORS['accent_blue']};")
        txid_lbl = QLabel(f"TXID: {record.txid}")
        txid_lbl.setStyleSheet(f"font-size: 11px; font-family: monospace; color: {THEME_COLORS['text_secondary']};")
        txid_lbl.setTextInteractionFlags(Qt.TextSelectableByMouse)
        title_box.addWidget(t_lbl)
        title_box.addWidget(txid_lbl)
        h_layout.addLayout(title_box)
        h_layout.addStretch()

        self.btn_copy_txid = QPushButton("📋 Copy Full TXID")
        self.btn_copy_txid.setCursor(Qt.PointingHandCursor)
        self.btn_copy_txid.setStyleSheet(f"""
            QPushButton {{
                background-color: {THEME_COLORS['bg_card']};
                border: 1px solid {THEME_COLORS['border_light']};
                color: {THEME_COLORS['text_primary']};
                padding: 6px 14px;
                border-radius: 4px;
                font-weight: 600;
                font-size: 11px;
            }}
            QPushButton:hover {{
                background-color: {THEME_COLORS['bg_card_alt']};
                border-color: {THEME_COLORS['accent_blue']};
            }}
        """)
        self.btn_copy_txid.clicked.connect(self._copy_txid)
        h_layout.addWidget(self.btn_copy_txid)

        dialog_layout.addWidget(header_frame)

        # Scroll Area for all content sections
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        content_widget = QWidget()
        layout = QVBoxLayout(content_widget)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(14)

        # 1. Section: Transaction Overview & Network Observation
        sec1_lbl = QLabel("1. LEDGER & NETWORK OBSERVATION")
        sec1_lbl.setStyleSheet(f"font-size: 11px; font-weight: 700; color: {THEME_COLORS['accent_blue']};")
        layout.addWidget(sec1_lbl)

        grid_frame = QFrame()
        grid_frame.setStyleSheet(f"background-color: {THEME_COLORS['bg_card']}; border: 1px solid {THEME_COLORS['border']}; border-radius: 6px; padding: 12px;")
        grid = QGridLayout(grid_frame)
        grid.setSpacing(10)

        grid.addWidget(QLabel("Observed Timestamp (UTC):"), 0, 0)
        grid.addWidget(QLabel(f"<b>{record.timestamp}</b>"), 0, 1)

        grid.addWidget(QLabel("Source Relay Node:"), 0, 2)
        grid.addWidget(QLabel(f"<b>{record.src_ip}:{record.src_port}</b>"), 0, 3)

        grid.addWidget(QLabel("Destination Node:"), 1, 0)
        grid.addWidget(QLabel(f"<b>{record.dst_ip}:{record.dst_port}</b>"), 1, 1)

        grid.addWidget(QLabel("Jurisdiction / ASN:"), 1, 2)
        grid.addWidget(QLabel(f"<b>{record.geo_country} • {record.asn}</b>"), 1, 3)

        grid.addWidget(QLabel("Script Encoding:"), 2, 0)
        grid.addWidget(QLabel(f"<b>{record.script_type}</b>"), 2, 1)

        grid.addWidget(QLabel("Miner Fee:"), 2, 2)
        grid.addWidget(QLabel(f"<b>{record.fee:.6f} BTC</b>"), 2, 3)

        grid.addWidget(QLabel("Total Output Volume:"), 3, 0)
        grid.addWidget(QLabel(f"<b>{record.total_output_amount:.4f} BTC</b>"), 3, 1)

        grid.addWidget(QLabel("Validation State:"), 3, 2)
        v_status = record.validation_status.value if hasattr(record.validation_status, "value") else str(record.validation_status)
        grid.addWidget(QLabel(f"<b>{v_status}</b>"), 3, 3)

        layout.addWidget(grid_frame)

        # 2. Section: Inputs and Outputs
        sec2_lbl = QLabel("2. SPENT INPUTS & OUTPUT DESTINATIONS")
        sec2_lbl.setStyleSheet(f"font-size: 11px; font-weight: 700; color: {THEME_COLORS['accent_purple']};")
        layout.addWidget(sec2_lbl)

        io_box = QHBoxLayout()
        io_box.setSpacing(12)

        # Inputs
        in_box = QVBoxLayout()
        in_lbl = QLabel(f"SPENT INPUTS ({len(record.input_addresses)})")
        in_lbl.setStyleSheet(f"font-size: 10px; font-weight: 700; color: {THEME_COLORS['accent_purple']};")
        in_txt = QTextEdit()
        in_txt.setReadOnly(True)
        in_txt.setMinimumHeight(110)
        in_txt.setStyleSheet(f"background-color: {THEME_COLORS['bg_card']}; border: 1px solid {THEME_COLORS['border']}; font-family: monospace; font-size: 11px; color: {THEME_COLORS['text_primary']};")
        in_lines = [
            f"{addr}  ({amt:.4f} BTC)"
            for addr, amt in zip(record.input_addresses, record.input_amounts)
        ]
        in_txt.setText("\n".join(in_lines) if in_lines else "None recorded (Coinbase or unlinked input)")
        in_box.addWidget(in_lbl)
        in_box.addWidget(in_txt)
        io_box.addLayout(in_box)

        # Outputs
        out_box = QVBoxLayout()
        out_lbl = QLabel(f"OUTPUT DESTINATIONS ({len(record.output_addresses)})")
        out_lbl.setStyleSheet(f"font-size: 10px; font-weight: 700; color: {THEME_COLORS['accent_amber']};")
        out_txt = QTextEdit()
        out_txt.setReadOnly(True)
        out_txt.setMinimumHeight(110)
        out_txt.setStyleSheet(f"background-color: {THEME_COLORS['bg_card']}; border: 1px solid {THEME_COLORS['border']}; font-family: monospace; font-size: 11px; color: {THEME_COLORS['text_primary']};")
        out_lines = [
            f"{addr}  ({amt:.4f} BTC)"
            for addr, amt in zip(record.output_addresses, record.output_amounts)
        ]
        out_txt.setText("\n".join(out_lines) if out_lines else "None recorded")
        out_box.addWidget(out_lbl)
        out_box.addWidget(out_txt)
        io_box.addLayout(out_box)

        layout.addLayout(io_box)

        # 3. Evidentiary Disclaimer
        disc_frame = QFrame()
        disc_frame.setStyleSheet(f"background-color: {THEME_COLORS['bg_card']}; border-left: 3px solid {THEME_COLORS['accent_amber']}; padding: 8px 12px; border-radius: 4px;")
        d_layout = QVBoxLayout(disc_frame)
        d_layout.setContentsMargins(0, 0, 0, 0)
        d_lbl = QLabel(
            "FORENSIC CHAIN NOTICE: Bitcoin transaction metadata reflects on-chain cryptographic settlement and P2P relay observation. "
            "Address linkage is heuristic; multi-signature wallets, CoinJoin mixes, and lightning payment channels require secondary corroboration."
        )
        d_lbl.setStyleSheet(f"color: {THEME_COLORS['text_muted']}; font-size: 10px; font-style: italic;")
        d_lbl.setWordWrap(True)
        d_layout.addWidget(d_lbl)
        layout.addWidget(disc_frame)

        scroll.setWidget(content_widget)
        dialog_layout.addWidget(scroll, 1)

        # Bottom Actions Bar
        act_box = QHBoxLayout()
        self.btn_copy_ip = QPushButton("📋 Copy Relay IP")
        self.btn_copy_ip.setCursor(Qt.PointingHandCursor)
        self.btn_copy_ip.clicked.connect(self._copy_ip)
        self.btn_copy_ip.setStyleSheet(f"""
            QPushButton {{
                background-color: {THEME_COLORS['bg_card']};
                border: 1px solid {THEME_COLORS['border_light']};
                color: {THEME_COLORS['text_primary']};
                padding: 6px 14px;
                border-radius: 4px;
                font-size: 11px;
            }}
            QPushButton:hover {{
                background-color: {THEME_COLORS['bg_card_alt']};
            }}
        """)
        act_box.addWidget(self.btn_copy_ip)
        act_box.addStretch()

        btn_close = QPushButton("Close Dossier")
        btn_close.setCursor(Qt.PointingHandCursor)
        btn_close.clicked.connect(self.accept)
        btn_close.setStyleSheet(f"""
            QPushButton {{
                background-color: {THEME_COLORS['bg_card']};
                border: 1px solid {THEME_COLORS['border_light']};
                color: {THEME_COLORS['text_primary']};
                padding: 6px 18px;
                border-radius: 4px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: {THEME_COLORS['bg_card_alt']};
                border-color: {THEME_COLORS['accent_blue']};
            }}
        """)
        act_box.addWidget(btn_close)
        dialog_layout.addLayout(act_box)

    def _copy_txid(self):
        clipboard = QApplication.clipboard()
        if clipboard:
            clipboard.setText(self.record.txid)
            self.btn_copy_txid.setText("✓ Copied TXID!")
            QTimer.singleShot(1800, lambda: self.btn_copy_txid.setText("📋 Copy Full TXID"))

    def _copy_ip(self):
        clipboard = QApplication.clipboard()
        if clipboard:
            clipboard.setText(self.record.src_ip)
            self.btn_copy_ip.setText("✓ Copied IP!")
            QTimer.singleShot(1800, lambda: self.btn_copy_ip.setText("📋 Copy Relay IP"))
