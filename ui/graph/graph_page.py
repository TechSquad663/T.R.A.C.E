"""Link Analysis and graph intelligence page."""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit,
    QFrame, QTextEdit, QComboBox
)
from PySide6.QtCore import Qt
from app.theme import THEME_COLORS
from core.constants import NODE_COLORS
from .graph_view import ForensicGraphView


class GraphPage(QWidget):
    """Link analysis workstation page featuring interactive network graph visualization."""

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(12)

        # Header Title
        title_box = QHBoxLayout()
        t_layout = QVBoxLayout()
        title = QLabel("LINK ANALYSIS & MULTI-HOP GRAPH RECONSTRUCTION")
        title.setStyleSheet(f"font-size: 16px; font-weight: 700; color: {THEME_COLORS['text_primary']};")
        subtitle = QLabel("Visual correlation across P2P broadcast nodes, cryptographic transactions, and resolved wallet entities.")
        subtitle.setStyleSheet(f"font-size: 11px; color: {THEME_COLORS['text_secondary']};")
        t_layout.addWidget(title)
        t_layout.addWidget(subtitle)
        title_box.addLayout(t_layout)
        title_box.addStretch()

        # Legend Bar
        legend_box = QHBoxLayout()
        legend_box.setSpacing(14)
        for ntype, color in NODE_COLORS.items():
            item_box = QHBoxLayout()
            item_box.setSpacing(5)
            dot = QLabel("●")
            dot.setStyleSheet(f"color: {color}; font-size: 14px;")
            lbl = QLabel(ntype)
            lbl.setStyleSheet(f"color: {THEME_COLORS['text_secondary']}; font-size: 11px; font-weight: 600;")
            item_box.addWidget(dot)
            item_box.addWidget(lbl)
            legend_box.addLayout(item_box)

        title_box.addLayout(legend_box)
        layout.addLayout(title_box)

        # Controls Toolbar
        toolbar = QFrame()
        toolbar.setStyleSheet(f"background-color: {THEME_COLORS['bg_card']}; border: 1px solid {THEME_COLORS['border']}; border-radius: 6px; padding: 6px 12px;")
        tb_layout = QHBoxLayout(toolbar)
        tb_layout.setContentsMargins(6, 4, 6, 4)
        tb_layout.setSpacing(10)

        self.search_node = QLineEdit()
        self.search_node.setPlaceholderText("Search node ID or address...")
        self.search_node.setStyleSheet(f"background-color: {THEME_COLORS['bg_dark']}; border: 1px solid {THEME_COLORS['border_light']}; border-radius: 4px; padding: 4px 8px;")
        self.search_node.returnPressed.connect(self._search_node_action)
        tb_layout.addWidget(self.search_node, 2)

        self.btn_1hop = QPushButton("1-Hop Neighborhood")
        self.btn_1hop.setStyleSheet("background-color: #1F2937; border: 1px solid #374151; color: white; padding: 5px 12px; border-radius: 4px; font-weight: 600;")
        self.btn_1hop.clicked.connect(lambda: self._apply_hop_filter(1))
        tb_layout.addWidget(self.btn_1hop)

        self.btn_2hop = QPushButton("2-Hop Neighborhood")
        self.btn_2hop.setStyleSheet("background-color: #1F2937; border: 1px solid #374151; color: white; padding: 5px 12px; border-radius: 4px; font-weight: 600;")
        self.btn_2hop.clicked.connect(lambda: self._apply_hop_filter(2))
        tb_layout.addWidget(self.btn_2hop)

        self.btn_reset = QPushButton("Reset Graph View")
        self.btn_reset.setStyleSheet("background-color: #1F2937; border: 1px solid #374151; color: white; padding: 5px 12px; border-radius: 4px; font-weight: 600;")
        self.btn_reset.clicked.connect(self._reset_view)
        tb_layout.addWidget(self.btn_reset)

        tb_layout.addStretch()

        self.btn_zoom_in = QPushButton("Zoom In (+)")
        self.btn_zoom_in.clicked.connect(lambda: self.graph_canvas.scale(1.2, 1.2))
        self.btn_zoom_out = QPushButton("Zoom Out (-)")
        self.btn_zoom_out.clicked.connect(lambda: self.graph_canvas.scale(0.83, 0.83))

        tb_layout.addWidget(self.btn_zoom_in)
        tb_layout.addWidget(self.btn_zoom_out)

        layout.addWidget(toolbar)

        # Graph View & Node Detail Drawer Split
        split_box = QHBoxLayout()
        split_box.setSpacing(12)

        self.graph_canvas = ForensicGraphView()
        self.graph_canvas.node_selected.connect(self._on_node_selected)
        split_box.addWidget(self.graph_canvas, 3)

        # Node Info Drawer
        self.drawer = QFrame()
        self.drawer.setStyleSheet(f"""
            background-color: {THEME_COLORS['bg_card']};
            border: 1px solid {THEME_COLORS['border']};
            border-radius: 8px;
            padding: 14px;
        """)
        d_layout = QVBoxLayout(self.drawer)
        d_layout.setContentsMargins(10, 10, 10, 10)
        d_layout.setSpacing(8)

        d_title = QLabel("INSPECTED NODE ATTRIBUTES")
        d_title.setStyleSheet(f"font-size: 11px; font-weight: 700; color: {THEME_COLORS['accent_blue']};")
        d_layout.addWidget(d_title)

        self.node_info_txt = QTextEdit()
        self.node_info_txt.setReadOnly(True)
        self.node_info_txt.setStyleSheet(f"background-color: {THEME_COLORS['bg_dark']}; border: 1px solid {THEME_COLORS['border']}; font-family: monospace; font-size: 11px;")
        self.node_info_txt.setText("Click on any node in the graph to inspect forensic attributes, transaction paths, and degree centrality.")
        d_layout.addWidget(self.node_info_txt)

        split_box.addWidget(self.drawer, 1)
        layout.addLayout(split_box)

        self.selected_node_id = None

    def update_data(self, pipeline):
        if not pipeline or not pipeline.graph:
            return
        self.graph_canvas.load_networkx_graph(pipeline.graph, max_nodes=120)

    def _on_node_selected(self, node_id: str, metadata: dict):
        self.selected_node_id = node_id
        lines = [
            f"NODE ID: {node_id}",
            f"TYPE   : {metadata.get('node_type', 'Unknown')}",
            f"LABEL  : {metadata.get('label', '')}",
            "-" * 35,
        ]
        for k, v in metadata.items():
            if k not in ["node_type", "label"]:
                lines.append(f"{k:<18}: {v}")
        self.node_info_txt.setText("\n".join(lines))

    def _apply_hop_filter(self, hops: int):
        if self.selected_node_id:
            self.graph_canvas.highlight_neighborhood(self.selected_node_id, hops=hops)

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
