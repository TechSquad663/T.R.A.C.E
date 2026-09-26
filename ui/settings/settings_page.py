"""Settings and System Administration Page."""
from pathlib import Path
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QDoubleSpinBox, QPushButton,
    QFrame, QTextEdit, QMessageBox
)
from PySide6.QtCore import Qt
from app.theme import THEME_COLORS
from config.settings import get_settings


class SettingsPage(QWidget):
    """Configuration, risk weights tuning, and offline health audit page."""

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(16)

        # Header Title
        title_box = QVBoxLayout()
        title = QLabel("SYSTEM CONFIGURATION & RISK ENGINE WEIGHTS")
        title.setStyleSheet(f"font-size: 16px; font-weight: 700; color: {THEME_COLORS['text_primary']};")
        subtitle = QLabel("Tune multi-signal risk fusion coefficients and review air-gapped system integrity logs.")
        subtitle.setStyleSheet(f"font-size: 11px; color: {THEME_COLORS['text_secondary']};")
        title_box.addWidget(title)
        title_box.addWidget(subtitle)
        layout.addLayout(title_box)

        # Risk Fusion Weights Card
        weights_card = QFrame()
        weights_card.setStyleSheet(f"background-color: {THEME_COLORS['bg_card']}; border: 1px solid {THEME_COLORS['border']}; border-radius: 8px; padding: 14px;")
        wc_layout = QVBoxLayout(weights_card)
        wc_layout.setSpacing(10)

        wc_title = QLabel("⚖️ RISK FUSION ENGINE COEFFICIENTS (Must sum to 1.00)")
        wc_title.setStyleSheet(f"font-size: 12px; font-weight: 700; color: {THEME_COLORS['accent_blue']};")
        wc_layout.addWidget(wc_title)

        spin_box = QHBoxLayout()
        spin_box.setSpacing(16)

        # Model weight
        w1_box = QVBoxLayout()
        w1_box.addWidget(QLabel("Supervised XGBoost Weight:"))
        self.spin_model = QDoubleSpinBox()
        self.spin_model.setRange(0.0, 1.0)
        self.spin_model.setSingleStep(0.05)
        self.spin_model.setValue(0.35)
        w1_box.addWidget(self.spin_model)
        spin_box.addLayout(w1_box)

        # Anomaly weight
        w2_box = QVBoxLayout()
        w2_box.addWidget(QLabel("Isolation Forest Weight:"))
        self.spin_anomaly = QDoubleSpinBox()
        self.spin_anomaly.setRange(0.0, 1.0)
        self.spin_anomaly.setSingleStep(0.05)
        self.spin_anomaly.setValue(0.25)
        w2_box.addWidget(self.spin_anomaly)
        spin_box.addLayout(w2_box)

        # Graph weight
        w3_box = QVBoxLayout()
        w3_box.addWidget(QLabel("Graph Topological Weight:"))
        self.spin_graph = QDoubleSpinBox()
        self.spin_graph.setRange(0.0, 1.0)
        self.spin_graph.setSingleStep(0.05)
        self.spin_graph.setValue(0.20)
        w3_box.addWidget(self.spin_graph)
        spin_box.addLayout(w3_box)

        # Network weight
        w4_box = QVBoxLayout()
        w4_box.addWidget(QLabel("Network Dispersion Weight:"))
        self.spin_network = QDoubleSpinBox()
        self.spin_network.setRange(0.0, 1.0)
        self.spin_network.setSingleStep(0.05)
        self.spin_network.setValue(0.20)
        w4_box.addWidget(self.spin_network)
        spin_box.addLayout(w4_box)

        wc_layout.addLayout(spin_box)

        btn_save_weights = QPushButton("Save Risk Weights")
        btn_save_weights.setStyleSheet("background-color: #2563EB; color: white; padding: 6px 16px; border-radius: 4px; font-weight: 700;")
        btn_save_weights.clicked.connect(self._save_weights)
        wc_layout.addWidget(btn_save_weights, alignment=Qt.AlignRight)

        layout.addWidget(weights_card)

        # Local GeoIP Status Card
        geo_card = QFrame()
        geo_card.setStyleSheet(f"background-color: {THEME_COLORS['bg_card']}; border: 1px solid {THEME_COLORS['border']}; border-radius: 8px; padding: 14px;")
        gc_layout = QVBoxLayout(geo_card)
        gc_layout.setSpacing(6)

        gc_title = QLabel("🌐 LOCAL GEOIP & ASN ENRICHMENT STATUS")
        gc_title.setStyleSheet(f"font-size: 12px; font-weight: 700; color: {THEME_COLORS['accent_emerald']};")
        gc_layout.addWidget(gc_title)

        settings = get_settings()
        geoip_dir = settings.GEOIP_DIR
        has_geoip = any(geoip_dir.glob("*.mmdb")) or any(geoip_dir.glob("*.csv"))
        status_text = "Local GeoIP Database Loaded (data/geoip/)" if has_geoip else "GeoIP enrichment unavailable (Preserving dataset country/asn metadata offline; no external lookups)"
        gc_desc = QLabel(status_text)
        gc_desc.setStyleSheet(f"color: {THEME_COLORS['text_secondary']}; font-size: 11px;")
        gc_layout.addWidget(gc_desc)

        layout.addWidget(geo_card)

        # System Log Tail
        log_lbl = QLabel("FORENSIC APPLICATION LOG STREAM (logs/trace.log)")
        log_lbl.setStyleSheet(f"font-size: 12px; font-weight: 700; color: {THEME_COLORS['text_primary']}; margin-top: 4px;")
        layout.addWidget(log_lbl)

        self.log_viewer = QTextEdit()
        self.log_viewer.setReadOnly(True)
        self.log_viewer.setStyleSheet(f"background-color: {THEME_COLORS['bg_card']}; border: 1px solid {THEME_COLORS['border']}; font-family: monospace; font-size: 11px;")
        layout.addWidget(self.log_viewer)

        # Refresh log button
        btn_refresh_log = QPushButton("🔄 Refresh Log Stream")
        btn_refresh_log.clicked.connect(self._refresh_log)
        layout.addWidget(btn_refresh_log, alignment=Qt.AlignRight)

        self._refresh_log()

    def _save_weights(self):
        tot = self.spin_model.value() + self.spin_anomaly.value() + self.spin_graph.value() + self.spin_network.value()
        if abs(tot - 1.0) > 0.01:
            QMessageBox.warning(self, "Invalid Weights", f"Weights must sum to 1.00 (Current total: {tot:.2f})")
            return
        settings = get_settings()
        settings.WEIGHT_MODEL_PROB = self.spin_model.value()
        settings.WEIGHT_ANOMALY_SCORE = self.spin_anomaly.value()
        settings.WEIGHT_GRAPH_SIGNAL = self.spin_graph.value()
        settings.WEIGHT_NETWORK_SIGNAL = self.spin_network.value()
        QMessageBox.information(self, "Saved", "Risk fusion engine weights updated.")

    def _refresh_log(self):
        log_file = get_settings().LOGS_DIR / "trace.log"
        if log_file.exists():
            try:
                with open(log_file, "r", encoding="utf-8", errors="replace") as f:
                    lines = f.readlines()
                    self.log_viewer.setText("".join(lines[-80:]))
            except Exception:
                self.log_viewer.setText("Unable to read log file.")
        else:
            self.log_viewer.setText("Log file not yet initialized.")
