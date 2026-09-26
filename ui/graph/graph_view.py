"""Interactive native PySide6 QGraphicsView link analysis graph canvas."""
import math
import logging
from typing import Dict, Any, List, Optional, Set
from PySide6.QtWidgets import (
    QGraphicsView, QGraphicsScene, QGraphicsItem, QGraphicsEllipseItem,
    QGraphicsLineItem, QGraphicsTextItem, QGraphicsRectItem, QToolTip
)
from PySide6.QtGui import QPen, QBrush, QColor, QFont, QPainter, QWheelEvent, QMouseEvent
from PySide6.QtCore import Qt, QPointF, QRectF, Signal
from app.theme import THEME_COLORS, theme_manager
from core.constants import NODE_COLORS, EDGE_COLORS

logger = logging.getLogger("TRACE.GraphView")


class GraphNodeItem(QGraphicsEllipseItem):
    """Visual interactive node in the link analysis graph."""

    def __init__(self, node_id: str, node_type: str, label: str, metadata: dict, parent_view):
        super().__init__(-18, -18, 36, 36)
        self.node_id = node_id
        self.node_type = node_type
        self.label_text = label
        self.metadata = metadata
        self.parent_view = parent_view

        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges, True)

        color_hex = NODE_COLORS.get(node_type, "#94A3B8")
        self.base_color = QColor(color_hex)
        self.setBrush(QBrush(self.base_color))

        # Text label below node
        self.text_item = QGraphicsTextItem(label, self)
        font = QFont("Helvetica", 8, QFont.Bold)
        self.text_item.setFont(font)
        self.text_item.setPos(-24, 18)

        # Tooltip
        tip_lines = [f"<b>{node_type.upper()}: {node_id}</b>"]
        for k, v in metadata.items():
            if k not in ["node_type", "label"]:
                tip_lines.append(f"{k}: {v}")
        self.setToolTip("<br>".join(tip_lines))

        self.edges: List["GraphEdgeItem"] = []
        self.refresh_theme()

    def refresh_theme(self):
        """Update node border and label color according to active theme."""
        is_dark = theme_manager.is_dark()
        if is_dark:
            self.setPen(QPen(QColor("#0F172A"), 2))
            self.text_item.setDefaultTextColor(QColor("#E2E8F0"))
        else:
            self.setPen(QPen(QColor("#CBD5E1"), 2))
            self.text_item.setDefaultTextColor(QColor("#0F172A"))

    def add_edge(self, edge: "GraphEdgeItem"):
        self.edges.append(edge)

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionHasChanged:
            for edge in self.edges:
                edge.update_position()
        return super().itemChange(change, value)

    def mousePressEvent(self, event: QMouseEvent):
        super().mousePressEvent(event)
        self.parent_view.node_selected.emit(self.node_id, self.metadata)


class GraphEdgeItem(QGraphicsLineItem):
    """Visual directed edge representing a forensic link between entities."""

    def __init__(self, source_item: GraphNodeItem, target_item: GraphNodeItem, edge_type: str, metadata: dict):
        super().__init__()
        self.source = source_item
        self.target = target_item
        self.edge_type = edge_type
        self.metadata = metadata

        color_hex = EDGE_COLORS.get(edge_type, "#64748B")
        self.base_color = QColor(color_hex)
        self.setPen(QPen(self.base_color, 1.5, Qt.SolidLine))
        self.setZValue(-1)  # Behind nodes

        self.source.add_edge(self)
        self.target.add_edge(self)
        self.update_position()

    def update_position(self):
        line = QPointF(self.target.pos() - self.source.pos())
        self.setLine(self.source.pos().x(), self.source.pos().y(), self.target.pos().x(), self.target.pos().y())


class ForensicGraphView(QGraphicsView):
    """Interactive canvas supporting zoom, pan, physics-inspired node placement, and path highlights."""

    node_selected = Signal(str, dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.setRenderHint(QPainter.Antialiasing)
        self.setDragMode(QGraphicsView.ScrollHandDrag)

        self.node_items: Dict[str, GraphNodeItem] = {}
        self.edge_items: List[GraphEdgeItem] = []

        self.refresh_theme()
        theme_manager.theme_changed.connect(lambda _: self.refresh_theme())

    def refresh_theme(self):
        """Update canvas background and node item styles for active theme."""
        bg_col = THEME_COLORS["bg_dark"]
        self.setStyleSheet(f"background-color: {bg_col}; border: none;")
        self.scene.setBackgroundBrush(QBrush(QColor(bg_col)))
        for item in self.node_items.values():
            item.refresh_theme()

    def clear_graph(self):
        self.scene.clear()
        self.node_items.clear()
        self.edge_items.clear()

    def load_networkx_graph(self, nx_graph, max_nodes: int = 150):
        """Construct visual elements from NetworkX graph with radial/force placement."""
        self.clear_graph()
        if not nx_graph or nx_graph.number_of_nodes() == 0:
            return

        # Select top nodes by degree to ensure smooth interactive rendering
        nodes = sorted(nx_graph.nodes(), key=lambda n: nx_graph.degree(n), reverse=True)[:max_nodes]
        subgraph = nx_graph.subgraph(nodes)

        # Circular / multi-tier layout calculation
        node_positions = {}
        total = len(nodes)
        radius_step = 60
        angle_step = (2 * math.pi) / max(1, total)

        for i, node in enumerate(nodes):
            tier = (i % 4) + 1
            rad = tier * radius_step + 40
            theta = i * angle_step * 2.3
            x = rad * math.cos(theta)
            y = rad * math.sin(theta)
            node_positions[node] = (x, y)

        # Create Visual Node Items
        for node in subgraph.nodes():
            data = subgraph.nodes[node]
            ntype = data.get("node_type", "wallet")
            label = data.get("label", str(node)[:12])
            pos = node_positions.get(node, (0, 0))

            item = GraphNodeItem(str(node), ntype, label, data, self)
            item.setPos(pos[0], pos[1])
            self.scene.addItem(item)
            self.node_items[str(node)] = item

        # Create Visual Edge Items
        for u, v, data in subgraph.edges(data=True):
            u, v = str(u), str(v)
            if u in self.node_items and v in self.node_items:
                etype = data.get("edge_type", "TRANSFER")
                edge_item = GraphEdgeItem(self.node_items[u], self.node_items[v], etype, data)
                self.scene.addItem(edge_item)
                self.edge_items.append(edge_item)

        self.setSceneRect(self.scene.itemsBoundingRect().adjusted(-60, -60, 60, 60))
        self.fitInView(self.sceneRect(), Qt.KeepAspectRatio)

    def wheelEvent(self, event: QWheelEvent):
        """Smooth mouse-wheel zoom."""
        zoom_in_factor = 1.15
        zoom_out_factor = 1.0 / zoom_in_factor

        if event.angleDelta().y() > 0:
            self.scale(zoom_in_factor, zoom_in_factor)
        else:
            self.scale(zoom_out_factor, zoom_out_factor)

    def highlight_neighborhood(self, root_node_id: str, hops: int = 1):
        """Highlight ego neighborhood around root_node_id and dim others."""
        if root_node_id not in self.node_items:
            return

        # Find 1-hop or 2-hop neighbors
        active_nodes = {root_node_id}
        frontier = {root_node_id}

        for _ in range(hops):
            next_frontier = set()
            for edge in self.edge_items:
                u_id = edge.source.node_id
                v_id = edge.target.node_id
                if u_id in frontier:
                    next_frontier.add(v_id)
                if v_id in frontier:
                    next_frontier.add(u_id)
            active_nodes.update(next_frontier)
            frontier = next_frontier

        # Apply visual focus
        for nid, item in self.node_items.items():
            if nid in active_nodes:
                item.setOpacity(1.0)
                item.setPen(QPen(QColor(THEME_COLORS["accent_blue"]), 3 if nid == root_node_id else 1.5))
            else:
                item.setOpacity(0.18)

        for edge in self.edge_items:
            if edge.source.node_id in active_nodes and edge.target.node_id in active_nodes:
                edge.setOpacity(1.0)
                edge.setPen(QPen(QColor(THEME_COLORS["accent_blue"]), 2))
            else:
                edge.setOpacity(0.08)

    def reset_highlight(self):
        """Reset all nodes and edges to standard visibility."""
        is_dark = theme_manager.is_dark()
        pen_color = QColor("#0F172A") if is_dark else QColor("#CBD5E1")
        for item in self.node_items.values():
            item.setOpacity(1.0)
            item.setPen(QPen(pen_color, 2))
        for edge in self.edge_items:
            edge.setOpacity(1.0)
            edge.setPen(QPen(edge.base_color, 1.5))
