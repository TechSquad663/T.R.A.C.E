"""Settings and System Administration Page with Theme Configuration and Scroll Responsiveness."""
from pathlib import Path
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QDoubleSpinBox, QPushButton,
    QFrame, QTextEdit, QMessageBox, QComboBox, QScrollArea, QApplication
)
from PySide6.QtCore import Qt, QTimer
from app.theme import THEME_COLORS, theme_manager
from config.settings import get_settings


from ui.components import ForensicComboBox


class SettingsPage(QWidget):
    """Configuration, risk weights tuning, theme selection, and offline health audit page."""

    def __init__(self):
        super().__init__()
        page_layout = QVBoxLayout(self)
        page_layout.setContentsMargins(0, 0, 0, 0)

        # Wrap in QScrollArea for responsiveness
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(16)

        # Header Title
        title_box = QVBoxLayout()
        self.title = QLabel("SYSTEM CONFIGURATION & WORKSTATION SETTINGS")
        self.subtitle = QLabel("Configure display themes, tune multi-signal risk fusion coefficients, and review air-gapped system logs.")
        title_box.addWidget(self.title)
        title_box.addWidget(self.subtitle)
        layout.addLayout(title_box)

        # Theme Configuration Card
        self.theme_card = QFrame()
        tc_layout = QVBoxLayout(self.theme_card)
        tc_layout.setSpacing(10)

        self.tc_title = QLabel("🎨 DISPLAY & WORKSTATION THEME")
        tc_layout.addWidget(self.tc_title)

        self.tc_desc = QLabel(
            "Select visual presentation mode. Dark Workstation provides low-glare focus for extended forensics sessions. "
            "Light Analyst delivers high contrast for briefing rooms, reports verification, and daylight operations."
        )
        self.tc_desc.setWordWrap(True)
        tc_layout.addWidget(self.tc_desc)

        th_row = QHBoxLayout()
        th_row.setSpacing(12)
        th_row.addWidget(QLabel("Active Theme Mode:"))

        self.theme_combo = ForensicComboBox()
        self.theme_combo.addItem("🌙 Dark Workstation (Deep Obsidian)", "dark")
        self.theme_combo.addItem("☀️ Light Analyst (Crisp Slate)", "light")
        self.theme_combo.setCurrentIndex(0 if theme_manager.is_dark() else 1)
        self.theme_combo.currentIndexChanged.connect(self._on_theme_combo_changed)
        th_row.addWidget(self.theme_combo)
        th_row.addStretch()

        tc_layout.addLayout(th_row)
        layout.addWidget(self.theme_card)

        # Risk Fusion Weights Card
        self.weights_card = QFrame()
        wc_layout = QVBoxLayout(self.weights_card)
        wc_layout.setSpacing(10)

        self.wc_title = QLabel("⚖️ RISK FUSION ENGINE COEFFICIENTS (Must sum to 1.00)")
        wc_layout.addWidget(self.wc_title)

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

        save_row = QHBoxLayout()
        self.lbl_weights_saved = QLabel("")
        self.lbl_weights_saved.setStyleSheet(f"color: {THEME_COLORS['accent_emerald']}; font-size: 11px; font-weight: 600;")
        save_row.addWidget(self.lbl_weights_saved)
        save_row.addStretch()

        self.btn_save_weights = QPushButton("Save Risk Weights")
        self.btn_save_weights.setCursor(Qt.PointingHandCursor)
        self.btn_save_weights.clicked.connect(self._save_weights)
        save_row.addWidget(self.btn_save_weights)
        wc_layout.addLayout(save_row)

        layout.addWidget(self.weights_card)

        # Local GeoIP Status Card
        self.geo_card = QFrame()
        gc_layout = QVBoxLayout(self.geo_card)
        gc_layout.setSpacing(6)

        self.gc_title = QLabel("🌐 LOCAL GEOIP & ASN ENRICHMENT STATUS")
        gc_layout.addWidget(self.gc_title)

        settings = get_settings()
        geoip_dir = settings.GEOIP_DIR
        has_geoip = any(geoip_dir.glob("*.mmdb")) or any(geoip_dir.glob("*.csv"))
        status_text = "Local GeoIP Database Loaded (data/geoip/)" if has_geoip else "GeoIP enrichment unavailable (Preserving dataset country/asn metadata offline; no external lookups)"
        self.gc_desc = QLabel(status_text)
        self.gc_desc.setWordWrap(True)
        gc_layout.addWidget(self.gc_desc)

        layout.addWidget(self.geo_card)

        # System Log Tail
        self.log_lbl = QLabel("FORENSIC APPLICATION LOG STREAM (logs/trace.log)")
        layout.addWidget(self.log_lbl)

        self.log_viewer = QTextEdit()
        self.log_viewer.setReadOnly(True)
        self.log_viewer.setMinimumHeight(140)
        layout.addWidget(self.log_viewer)

        # Refresh log button
        self.btn_refresh_log = QPushButton("🔄 Refresh Log Stream")
        self.btn_refresh_log.setCursor(Qt.PointingHandCursor)
        self.btn_refresh_log.clicked.connect(self._refresh_log)
        layout.addWidget(self.btn_refresh_log, alignment=Qt.AlignRight)

        layout.addStretch()

        scroll.setWidget(content)
        page_layout.addWidget(scroll)

        self.refresh_theme()
        theme_manager.theme_changed.connect(self._on_theme_manager_changed)

        self._refresh_log()

    def _on_theme_combo_changed(self, index: int):
        theme_name = self.theme_combo.currentData()
        if theme_name:
            theme_manager.set_theme(theme_name)

    def _on_theme_manager_changed(self, theme_name: str):
        # Sync combo selection
        self.theme_combo.blockSignals(True)
        idx = 0 if theme_name == "dark" else 1
        self.theme_combo.setCurrentIndex(idx)
        self.theme_combo.blockSignals(False)
        self.refresh_theme()

    def refresh_theme(self):
        """Update element styling according to active theme."""
        is_dark = theme_manager.is_dark()
        self.title.setStyleSheet(f"font-size: 16px; font-weight: 700; color: {THEME_COLORS['text_primary']};")
        self.subtitle.setStyleSheet(f"font-size: 11px; color: {THEME_COLORS['text_secondary']};")

        # Theme card styling
        self.theme_card.setStyleSheet(f"background-color: {THEME_COLORS['bg_card']}; border: 1px solid {THEME_COLORS['border']}; border-radius: 8px; padding: 14px;")
        self.tc_title.setStyleSheet(f"font-size: 12px; font-weight: 700; color: {THEME_COLORS['accent_purple']};")
        self.tc_desc.setStyleSheet(f"color: {THEME_COLORS['text_secondary']}; font-size: 11px;")

        # Weights card styling
        self.weights_card.setStyleSheet(f"background-color: {THEME_COLORS['bg_card']}; border: 1px solid {THEME_COLORS['border']}; border-radius: 8px; padding: 14px;")
        self.wc_title.setStyleSheet(f"font-size: 12px; font-weight: 700; color: {THEME_COLORS['accent_blue']};")
        self.btn_save_weights.setStyleSheet(f"""
            QPushButton {{
                background-color: {THEME_COLORS['accent_blue']};
                color: white;
                padding: 6px 16px;
                border: none;
                border-radius: 4px;
                font-weight: 700;
            }}
            QPushButton:hover {{
                background-color: {"#1D4ED8" if is_dark else "#0369A1"};
            }}
        """)

        # Geo card styling
        self.geo_card.setStyleSheet(f"background-color: {THEME_COLORS['bg_card']}; border: 1px solid {THEME_COLORS['border']}; border-radius: 8px; padding: 14px;")
        self.gc_title.setStyleSheet(f"font-size: 12px; font-weight: 700; color: {THEME_COLORS['accent_emerald']};")
        self.gc_desc.setStyleSheet(f"color: {THEME_COLORS['text_secondary']}; font-size: 11px;")

        # Log viewer styling
        self.log_lbl.setStyleSheet(f"font-size: 12px; font-weight: 700; color: {THEME_COLORS['text_primary']}; margin-top: 4px;")
        self.log_viewer.setStyleSheet(f"background-color: {THEME_COLORS['bg_card']}; border: 1px solid {THEME_COLORS['border']}; color: {THEME_COLORS['text_primary']}; font-family: monospace; font-size: 11px;")
        self.btn_refresh_log.setStyleSheet(f"background-color: {THEME_COLORS['bg_card']}; border: 1px solid {THEME_COLORS['border_light']}; color: {THEME_COLORS['text_primary']}; padding: 6px 14px; border-radius: 4px;")

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
        self.lbl_weights_saved.setText("✓ Weights saved successfully!")
        QTimer.singleShot(3000, lambda: self.lbl_weights_saved.setText(""))
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
