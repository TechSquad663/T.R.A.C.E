"""Forensic visualization components rendered natively with PySide6 QPainter."""
import math
from typing import List, Tuple, Dict, Any, Optional
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame
from PySide6.QtCore import Qt, QRectF, QPointF
from PySide6.QtGui import QPainter, QPen, QBrush, QColor, QFont, QLinearGradient, QPainterPath
from app.theme import THEME_COLORS, theme_manager


class ForensicCard(QFrame):
    """Container frame for charts and analytics widgets."""

    def __init__(self, title: str, subtitle: str = ""):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(14, 12, 14, 12)
        self.layout.setSpacing(8)

        header_layout = QVBoxLayout()
        header_layout.setSpacing(2)
        self.lbl_title = QLabel(title.upper())
        header_layout.addWidget(self.lbl_title)

        if subtitle:
            self.lbl_sub = QLabel(subtitle)
            header_layout.addWidget(self.lbl_sub)
        else:
            self.lbl_sub = None

        self.layout.addLayout(header_layout)
        self.refresh_theme()
        theme_manager.theme_changed.connect(lambda _: self.refresh_theme())

    def add_widget(self, widget: QWidget):
        self.layout.addWidget(widget)

    def refresh_theme(self):
        self.setStyleSheet(f"""
            ForensicCard {{
                background-color: {THEME_COLORS['bg_card']};
                border: 1px solid {THEME_COLORS['border']};
                border-radius: 8px;
            }}
        """)
        self.lbl_title.setStyleSheet(f"font-size: 11px; font-weight: 700; color: {THEME_COLORS['text_primary']}; letter-spacing: 0.5px;")
        if self.lbl_sub:
            self.lbl_sub.setStyleSheet(f"font-size: 10px; color: {THEME_COLORS['text_secondary']};")


class DonutChartWidget(QWidget):
    """Crisp vector donut chart displaying distribution slices with side legend."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.slices: List[Tuple[str, float, str]] = []  # (label, value, hex_color)
        self.setMinimumSize(220, 150)
        theme_manager.theme_changed.connect(lambda _: self.update())

    def set_data(self, slices: List[Tuple[str, float, str]]):
        self.slices = slices
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        w = self.width()
        h = self.height()
        total = sum(s[1] for s in self.slices)

        if total <= 0:
            painter.setPen(QColor(THEME_COLORS["text_muted"]))
            font = QFont("Segoe UI", 10)
            painter.setFont(font)
            painter.drawText(self.rect(), Qt.AlignCenter, "No distribution data available")
            return

        # Allocate left 45% for donut, right 55% for legend
        donut_size = min(w * 0.42, h - 20)
        center_x = 10 + donut_size / 2
        center_y = h / 2
        radius = donut_size / 2
        inner_radius = radius * 0.62

        donut_rect = QRectF(center_x - radius, center_y - radius, radius * 2, radius * 2)

        start_angle = 90.0 * 16  # 12 o'clock in 1/16th of a degree
        for label, val, color_hex in self.slices:
            if val <= 0:
                continue
            span_angle = -(val / total) * 360.0 * 16
            painter.setBrush(QBrush(QColor(color_hex)))
            painter.setPen(Qt.NoPen)
            painter.drawPie(donut_rect, int(start_angle), int(span_angle))
            start_angle += span_angle

        # Inner cutout for donut effect
        hole_rect = QRectF(center_x - inner_radius, center_y - inner_radius, inner_radius * 2, inner_radius * 2)
        painter.setBrush(QBrush(QColor(THEME_COLORS["bg_card"])))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(hole_rect)

        # Center label (Total count)
        painter.setPen(QColor(THEME_COLORS["text_primary"]))
        center_font = QFont("Segoe UI", 11, QFont.Bold)
        painter.setFont(center_font)
        painter.drawText(hole_rect, Qt.AlignCenter, str(int(total)))

        # Legend on the right
        legend_x = center_x + radius + 14
        avail_legend_w = max(60, w - legend_x - 10)
        legend_y = max(10, int((h - (len(self.slices) * 22)) / 2))
        font_leg = QFont("Segoe UI", 9)
        painter.setFont(font_leg)
        fm = painter.fontMetrics()

        val_w = 46
        lbl_w = max(35, avail_legend_w - val_w - 18)

        for label, val, color_hex in self.slices:
            pct = (val / total * 100.0) if total > 0 else 0.0
            # Color swatch
            painter.setBrush(QBrush(QColor(color_hex)))
            painter.setPen(Qt.NoPen)
            painter.drawRoundedRect(QRectF(legend_x, legend_y + 4, 9, 9), 2, 2)

            # Elided Label
            label_rect = QRectF(legend_x + 14, legend_y, lbl_w, 18)
            elided_lbl = fm.elidedText(label, Qt.ElideRight, int(lbl_w))
            painter.setPen(QColor(THEME_COLORS["text_secondary"]))
            painter.drawText(label_rect, Qt.AlignLeft | Qt.AlignVCenter, elided_lbl)

            # Value string
            val_rect = QRectF(legend_x + 14 + lbl_w + 2, legend_y, val_w, 18)
            painter.setPen(QColor(THEME_COLORS["text_primary"]))
            val_str = f"{int(val)} ({pct:.0f}%)"
            painter.drawText(val_rect, Qt.AlignRight | Qt.AlignVCenter, val_str)

            legend_y += 22


class ActivityLineChartWidget(QWidget):
    """Vector time-series chart showing transaction activity over temporal intervals."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.data_points: List[Tuple[str, float]] = []  # (bucket_label, count)
        self.setMinimumSize(250, 150)
        theme_manager.theme_changed.connect(lambda _: self.update())

    def set_data(self, points: List[Tuple[str, float]]):
        self.data_points = points
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        w = self.width()
        h = self.height()

        if not self.data_points or max((p[1] for p in self.data_points), default=0) == 0:
            painter.setPen(QColor(THEME_COLORS["text_muted"]))
            font = QFont("Segoe UI", 10)
            painter.setFont(font)
            painter.drawText(self.rect(), Qt.AlignCenter, "No temporal activity data available")
            return

        # Margins
        left = 40
        right = 20
        top = 20
        bottom = 30
        plot_w = w - left - right
        plot_h = h - top - bottom
        if plot_w <= 20 or plot_h <= 20:
            return

        max_val = max(p[1] for p in self.data_points)
        if max_val == 0:
            max_val = 1.0

        # Draw grid lines
        grid_pen = QPen(QColor(THEME_COLORS["border"]))
        grid_pen.setStyle(Qt.DashLine)
        painter.setPen(grid_pen)
        painter.setFont(QFont("Segoe UI", 8))

        steps = 4
        for i in range(steps + 1):
            y = top + plot_h - (i * plot_h / steps)
            val = i * max_val / steps
            painter.drawLine(left, int(y), left + plot_w, int(y))
            painter.setPen(QColor(THEME_COLORS["text_muted"]))
            painter.drawText(5, int(y + 4), f"{int(val)}")
            painter.setPen(grid_pen)

        # Calculate coordinates
        coords = []
        n = len(self.data_points)
        x_step = plot_w / max(1, n - 1) if n > 1 else plot_w / 2

        for i, (label, val) in enumerate(self.data_points):
            cx = left + (i * x_step)
            cy = top + plot_h - (val / max_val * plot_h)
            coords.append((cx, cy))

        # Fill gradient under curve
        path = QPainterPath()
        path.moveTo(coords[0][0], top + plot_h)
        for cx, cy in coords:
            path.lineTo(cx, cy)
        path.lineTo(coords[-1][0], top + plot_h)
        path.closeSubpath()

        grad = QLinearGradient(0, top, 0, top + plot_h)
        fill_col_top = QColor(THEME_COLORS["accent_blue"])
        fill_col_top.setAlpha(60)
        fill_col_bot = QColor(THEME_COLORS["accent_blue"])
        fill_col_bot.setAlpha(0)
        grad.setColorAt(0.0, fill_col_top)
        grad.setColorAt(1.0, fill_col_bot)

        painter.setBrush(QBrush(grad))
        painter.setPen(Qt.NoPen)
        painter.drawPath(path)

        # Draw main line
        line_pen = QPen(QColor(THEME_COLORS["accent_blue"]), 2.2)
        painter.setPen(line_pen)
        for i in range(len(coords) - 1):
            painter.drawLine(int(coords[i][0]), int(coords[i][1]), int(coords[i + 1][0]), int(coords[i + 1][1]))

        # Draw dots & X labels
        dot_brush = QBrush(QColor(THEME_COLORS["accent_blue"]))
        white_brush = QBrush(QColor("#FFFFFF"))
        painter.setFont(QFont("Segoe UI", 8))
        label_interval = max(1, n // 5)

        for i, (cx, cy) in enumerate(coords):
            # Point dot
            painter.setBrush(white_brush)
            painter.setPen(line_pen)
            painter.drawEllipse(QPointF(cx, cy), 3.5, 3.5)

            # X Axis Label
            if i % label_interval == 0 or i == n - 1:
                lbl = self.data_points[i][0]
                painter.setPen(QColor(THEME_COLORS["text_secondary"]))
                painter.drawText(QRectF(cx - 30, top + plot_h + 8, 60, 16), Qt.AlignCenter, lbl)


class HorizontalBarChartWidget(QWidget):
    """Horizontal stacked / proportional bar chart for patterns and jurisdictions."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.items: List[Tuple[str, float, str]] = []  # (label, value, hex_color)
        self.setMinimumSize(220, 150)
        theme_manager.theme_changed.connect(lambda _: self.update())

    def set_data(self, items: List[Tuple[str, float, str]]):
        self.items = items
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        w = self.width()
        h = self.height()

        if not self.items or max((item[1] for item in self.items), default=0) == 0:
            painter.setPen(QColor(THEME_COLORS["text_muted"]))
            font = QFont("Segoe UI", 10)
            painter.setFont(font)
            painter.drawText(self.rect(), Qt.AlignCenter, "No categorical data detected")
            return

        max_val = max(item[1] for item in self.items)
        if max_val == 0:
            max_val = 1.0

        bar_height = 14
        row_spacing = 26
        left_label_w = min(115, max(75, int(w * 0.30)))
        right_val_w = 40
        available_bar_w = max(20, w - left_label_w - right_val_w - 20)

        y = 10
        painter.setFont(QFont("Segoe UI", 9))
        fm = painter.fontMetrics()

        for label, val, color_hex in self.items:
            # Draw label with elision protection
            painter.setPen(QColor(THEME_COLORS["text_secondary"]))
            elided_label = fm.elidedText(label, Qt.ElideRight, int(left_label_w - 10))
            painter.drawText(QRectF(8, y, left_label_w - 10, bar_height + 4), Qt.AlignLeft | Qt.AlignVCenter, elided_label)

            # Draw bar background track
            track_rect = QRectF(left_label_w, y + 2, available_bar_w, bar_height)
            painter.setBrush(QBrush(QColor(THEME_COLORS["border"])))
            painter.setPen(Qt.NoPen)
            painter.drawRoundedRect(track_rect, 4, 4)

            # Draw filled portion
            fill_w = max(4.0, (val / max_val) * available_bar_w)
            fill_rect = QRectF(left_label_w, y + 2, fill_w, bar_height)
            painter.setBrush(QBrush(QColor(color_hex)))
            painter.drawRoundedRect(fill_rect, 4, 4)

            # Draw count value
            painter.setPen(QColor(THEME_COLORS["text_primary"]))
            painter.drawText(QRectF(left_label_w + available_bar_w + 8, y, right_val_w, bar_height + 4), Qt.AlignLeft | Qt.AlignVCenter, str(int(val)))

            y += row_spacing
            if y + row_spacing > h:
                break
