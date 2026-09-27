"""Link Analysis and graph intelligence page with multi-hop propagation."""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit,
    QFrame, QTextEdit, QComboBox, QMessageBox, QSplitter
)
from PySide6.QtCore import Qt
from app.theme import THEME_COLORS, theme_manager
from core.constants import NODE_COLORS
from graph.path_analysis import PathAnalyzer
from .graph_view import ForensicGraphView


class GraphPage(QWidget):
    """Link analysis workstation page featuring interactive network graph visualization."""

    def __init__(self):
        super().__init__()
        self.pipeline = None
        self.selected_node_id = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(12)

        # Header Title
        title_box = QVBoxLayout()
        self.title = QLabel("LINK ANALYSIS & MULTI-HOP GRAPH RECONSTRUCTION")
        self.subtitle = QLabel("Visual correlation across P2P broadcast nodes, cryptographic transactions, and resolved wallet entities.")
        title_box.addWidget(self.title)
        title_box.addWidget(self.subtitle)
        layout.addLayout(title_box)

        # Controls Toolbar
        self.toolbar = QFrame()
        tb_layout = QHBoxLayout(self.toolbar)
        tb_layout.setContentsMargins(8, 6, 8, 6)
        tb_layout.setSpacing(8)

        self.search_node = QLineEdit()
        self.search_node.setPlaceholderText("Search node ID, wallet address, or IP...")
        self.search_node.setMinimumWidth(160)
        self.search_node.returnPressed.connect(self._search_node_action)
        tb_layout.addWidget(self.search_node, 1)

        self.btn_1hop = QPushButton("1-Hop")
        self.btn_1hop.setCursor(Qt.PointingHandCursor)
        self.btn_1hop.setToolTip("Filter to 1-hop direct neighbors of selected node")
        self.btn_1hop.clicked.connect(lambda: self._apply_hop_filter(1))
        tb_layout.addWidget(self.btn_1hop)

        self.btn_2hop = QPushButton("2-Hop")
        self.btn_2hop.setCursor(Qt.PointingHandCursor)
        self.btn_2hop.setToolTip("Filter to 2-hop neighborhood of selected node")
        self.btn_2hop.clicked.connect(lambda: self._apply_hop_filter(2))
        tb_layout.addWidget(self.btn_2hop)

        self.btn_propagate = QPushButton("🌱 Propagate Seed Risk")
        self.btn_propagate.setCursor(Qt.PointingHandCursor)
        self.btn_propagate.setToolTip("Run Personalized PageRank risk taint decay from selected node")
        self.btn_propagate.clicked.connect(self._propagate_seed_action)
        tb_layout.addWidget(self.btn_propagate)

        self.btn_reset = QPushButton("Reset")
        self.btn_reset.setCursor(Qt.PointingHandCursor)
        self.btn_reset.clicked.connect(self._reset_view)
        tb_layout.addWidget(self.btn_reset)

        self.btn_fit = QPushButton("Fit to View")
        self.btn_fit.setCursor(Qt.PointingHandCursor)
        self.btn_fit.setToolTip("Fit all graph elements to current viewport")
        self.btn_fit.clicked.connect(lambda: self.graph_canvas.fit_to_view())
        tb_layout.addWidget(self.btn_fit)

        tb_layout.addStretch()

        self.btn_zoom_in = QPushButton("Zoom In (+)")
        self.btn_zoom_in.setCursor(Qt.PointingHandCursor)
        self.btn_zoom_in.clicked.connect(lambda: self.graph_canvas.scale(1.2, 1.2))
        tb_layout.addWidget(self.btn_zoom_in)

        self.btn_zoom_out = QPushButton("Zoom Out (-)")
        self.btn_zoom_out.setCursor(Qt.PointingHandCursor)
        self.btn_zoom_out.clicked.connect(lambda: self.graph_canvas.scale(0.83, 0.83))
        tb_layout.addWidget(self.btn_zoom_out)

        layout.addWidget(self.toolbar)

        # Dedicated Graph Legend Bar
        self.legend_bar = QFrame()
        lb_layout = QHBoxLayout(self.legend_bar)
        lb_layout.setContentsMargins(10, 4, 10, 4)
        lb_layout.setSpacing(16)

        lbl_leg_title = QLabel("NODE CLASSIFICATION:")
        lbl_leg_title.setStyleSheet(f"font-size: 10px; font-weight: 700; color: {THEME_COLORS['text_muted']}; letter-spacing: 0.5px;")
        lb_layout.addWidget(lbl_leg_title)

        self.legend_labels = []
        for ntype, color in NODE_COLORS.items():
            item_box = QHBoxLayout()
            item_box.setSpacing(5)
            dot = QLabel("●")
            dot.setStyleSheet(f"color: {color}; font-size: 13px;")
            lbl = QLabel(ntype)
            item_box.addWidget(dot)
            item_box.addWidget(lbl)
            lb_layout.addLayout(item_box)
            self.legend_labels.append(lbl)

        lb_layout.addStretch()
        layout.addWidget(self.legend_bar)

        # Graph View & Node Detail Drawer Splitter (User Resizable)
        self.splitter = QSplitter(Qt.Horizontal)
        self.splitter.setChildrenCollapsible(False)

        self.graph_canvas = ForensicGraphView()
        self.graph_canvas.setMinimumWidth(380)
        self.graph_canvas.node_selected.connect(self._on_node_selected)
        self.splitter.addWidget(self.graph_canvas)

        # Node Info Drawer
        self.drawer = QFrame()
        self.drawer.setMinimumWidth(260)
        self.drawer.setMaximumWidth(400)
        d_layout = QVBoxLayout(self.drawer)
        d_layout.setContentsMargins(12, 12, 12, 12)
        d_layout.setSpacing(8)

        self.d_title = QLabel("INSPECTED NODE & GRAPH METRICS")
        d_layout.addWidget(self.d_title)

        self.node_info_txt = QTextEdit()
        self.node_info_txt.setReadOnly(True)
        self.node_info_txt.setText("Click on any node in the graph or select a seed entity to inspect topological metrics, multi-hop flow paths, and investigative leads.")
        d_layout.addWidget(self.node_info_txt)

        self.splitter.addWidget(self.drawer)
        self.splitter.setStretchFactor(0, 3)
        self.splitter.setStretchFactor(1, 1)
        self.splitter.setSizes([750, 320])

        layout.addWidget(self.splitter, 1)

        self.refresh_theme()
        theme_manager.theme_changed.connect(lambda _: self.refresh_theme())

    def showEvent(self, event):
        super().showEvent(event)
        # Ensure proper initial split when page is displayed
        w = self.splitter.width()
        if w > 400:
            drawer_w = min(350, int(w * 0.30))
            self.splitter.setSizes([w - drawer_w, drawer_w])
        from PySide6.QtCore import QTimer
        QTimer.singleShot(60, self.graph_canvas.fit_to_view)

    def refresh_theme(self):
        """Update element styling according to active theme."""
        self.title.setStyleSheet(f"font-size: 16px; font-weight: 700; color: {THEME_COLORS['text_primary']};")
        self.subtitle.setStyleSheet(f"font-size: 11px; color: {THEME_COLORS['text_secondary']};")

        for lbl in self.legend_labels:
            lbl.setStyleSheet(f"color: {THEME_COLORS['text_secondary']}; font-size: 11px; font-weight: 600;")

        self.toolbar.setStyleSheet(f"background-color: {THEME_COLORS['bg_card']}; border: 1px solid {THEME_COLORS['border']}; border-radius: 6px; padding: 4px 8px;")
        self.legend_bar.setStyleSheet(f"background-color: {THEME_COLORS['bg_dark']}; border: 1px solid {THEME_COLORS['border']}; border-radius: 4px;")
        self.search_node.setStyleSheet(f"background-color: {THEME_COLORS['bg_dark']}; border: 1px solid {THEME_COLORS['border_light']}; border-radius: 4px; padding: 4px 8px; color: {THEME_COLORS['text_primary']};")

        btn_style = f"background-color: {THEME_COLORS['bg_card']}; border: 1px solid {THEME_COLORS['border_light']}; color: {THEME_COLORS['text_primary']}; padding: 5px 12px; border-radius: 4px; font-weight: 600;"
        self.btn_1hop.setStyleSheet(btn_style)
        self.btn_2hop.setStyleSheet(btn_style)
        self.btn_propagate.setStyleSheet(f"background-color: {THEME_COLORS['accent_orange']}; color: #FFFFFF; border: none; padding: 5px 12px; border-radius: 4px; font-weight: 700;")
        self.btn_reset.setStyleSheet(btn_style)
        self.btn_fit.setStyleSheet(btn_style)
        self.btn_zoom_in.setStyleSheet(btn_style)
        self.btn_zoom_out.setStyleSheet(btn_style)

        self.drawer.setStyleSheet(f"""
            background-color: {THEME_COLORS['bg_card']};
            border: 1px solid {THEME_COLORS['border']};
            border-radius: 8px;
            padding: 14px;
        """)
        self.d_title.setStyleSheet(f"font-size: 11px; font-weight: 700; color: {THEME_COLORS['accent_blue']}; letter-spacing: 0.5px;")
        self.node_info_txt.setStyleSheet(f"background-color: {THEME_COLORS['bg_dark']}; border: 1px solid {THEME_COLORS['border']}; color: {THEME_COLORS['text_primary']}; font-family: 'Consolas', 'Courier New', monospace; font-size: 11px; line-height: 16px;")

    def update_data(self, pipeline):
        self.pipeline = pipeline
        if not pipeline or not pipeline.graph:
            return
        self.graph_canvas.load_networkx_graph(pipeline.graph, max_nodes=150)

    def _on_node_selected(self, node_id: str, metadata: dict):
        self.selected_node_id = node_id
        lines = [
            f"=== FORENSIC NODE INSPECTION ===",
            f"NODE ID  : {node_id}",
            f"TYPE     : {metadata.get('node_type', 'Unknown').upper()}",
            f"LABEL    : {metadata.get('label', '')}",
            "-" * 38,
            "TOPOLOGICAL METRICS:",
        ]

        if self.pipeline and self.pipeline.graph and self.pipeline.graph.has_node(node_id):
            g = self.pipeline.graph
            deg = g.degree(node_id)
            in_deg = g.in_degree(node_id) if hasattr(g, "in_degree") else "N/A"
            out_deg = g.out_degree(node_id) if hasattr(g, "out_degree") else "N/A"
            lines.append(f"  • Total Degree  : {deg}")
            lines.append(f"  • In-Degree     : {in_deg}")
            lines.append(f"  • Out-Degree    : {out_deg}")

        lines.append("-" * 38)
        lines.append("METADATA ATTRIBUTES:")
        for k, v in metadata.items():
            if k not in ["node_type", "label"]:
                lines.append(f"  • {k:<15}: {v}")

        lines.append("-" * 38)
        lines.append("💡 Click '🌱 Propagate Seed Risk' to compute multi-hop taint decay from this entity.")
        self.node_info_txt.setText("\n".join(lines))

    def _apply_hop_filter(self, hops: int):
        if self.selected_node_id:
            self.graph_canvas.highlight_neighborhood(self.selected_node_id, hops=hops)
        else:
            QMessageBox.information(self, "Selection Required", "Please click on a graph node first to explore its neighborhood.")

    def _propagate_seed_action(self):
        seed_id = self.selected_node_id or self.search_node.text().strip()
        if not seed_id:
            QMessageBox.information(self, "Seed Required", "Please click on a node or enter an address in the search box to act as the seed wallet.")
            return

        if not self.pipeline or not self.pipeline.graph or not self.pipeline.graph.has_node(seed_id):
            QMessageBox.warning(self, "Node Not in Graph", f"The node '{seed_id}' was not found in the current graph topology.")
            return

        analyzer = PathAnalyzer(self.pipeline.graph)
        taint_scores = analyzer.propagate_seed_taint([seed_id])
        self.graph_canvas.highlight_taint(taint_scores)

        # Ranked reachable nodes
        sorted_taint = sorted(
            [(n, s) for n, s in taint_scores.items() if s > 0.05 and n != seed_id],
            key=lambda x: x[1],
            reverse=True
        )[:10]

        lines = [
            "========================================",
            "SEED WALLET RISK PROPAGATION RESULTS",
            f"Seed Node  : {seed_id}",
            "Algorithm  : Personalized PageRank Decay",
            f"Total Nodes: {len(self.pipeline.graph.nodes())}",
            "----------------------------------------",
            "TOP PROPAGATED RISK FLOWS:",
        ]
        for target, score in sorted_taint:
            lines.append(f"  • {target[:20]:<20} Taint: {score:.3f}")

        lines.extend([
            "----------------------------------------",
            "⚠️ ANALYTICAL SIGNAL DISCLAIMER:",
            "Propagated risk scores represent algorithmic",
            "proximity in transaction topology. They do NOT",
            "constitute legal proof of ownership, criminal",
            "conspiracy, or illicit activity.",
            "========================================"
        ])
        self.node_info_txt.setText("\n".join(lines))

    def _reset_view(self):
        self.graph_canvas.reset_highlight()
        self.selected_node_id = None
        self.node_info_txt.setText("Graph view reset. Select a node to inspect attributes.")

    def _search_node_action(self):
        query = self.search_node.text().strip()
        if not query:
            return
        for nid in self.graph_canvas.node_items.keys():
            if query.lower() in nid.lower():
                self.selected_node_id = nid
                self.graph_canvas.highlight_neighborhood(nid, hops=1)
                item = self.graph_canvas.node_items[nid]
                self._on_node_selected(nid, item.metadata)
                break
        else:
            QMessageBox.information(self, "Node Not Found", f"No visible node matches '{query}'.")
