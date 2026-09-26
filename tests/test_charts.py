"""Unit tests for forensic charts and overview dashboard."""
import os
import pytest
from PySide6.QtWidgets import QApplication
from ui.charts import DonutChartWidget, ActivityLineChartWidget, HorizontalBarChartWidget, ForensicCard
from ui.overview.overview_page import OverviewPage
from pipeline.investigation_pipeline import InvestigationPipeline
from generator.synthetic_dataset import SyntheticBitcoinTrafficGenerator
from app.theme import theme_manager


@pytest.fixture(scope="session")
def qapp():
    os.environ["QT_QPA_PLATFORM"] = "offscreen"
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_donut_chart_widget(qapp):
    widget = DonutChartWidget()
    widget.resize(300, 200)

    # Empty paint
    widget.repaint()

    # Populated paint
    slices = [
        ("Critical", 10.0, "#EF4444"),
        ("High", 25.0, "#F97316"),
        ("Medium", 40.0, "#F59E0B"),
        ("Low", 25.0, "#10B981"),
    ]
    widget.set_data(slices)
    widget.repaint()
    assert widget.slices == slices


def test_activity_line_chart_widget(qapp):
    widget = ActivityLineChartWidget()
    widget.resize(400, 200)

    # Empty paint
    widget.repaint()

    # Populated paint
    points = [
        ("10:00", 5.0),
        ("10:15", 18.0),
        ("10:30", 42.0),
        ("10:45", 27.0),
        ("11:00", 35.0),
    ]
    widget.set_data(points)
    widget.repaint()
    assert len(widget.data_points) == 5


def test_horizontal_bar_chart_widget(qapp):
    widget = HorizontalBarChartWidget()
    widget.resize(350, 200)

    # Empty paint
    widget.repaint()

    # Populated paint
    items = [
        ("Peeling Chain", 12.0, "#EF4444"),
        ("High Fan-Out", 8.0, "#F97316"),
        ("Rapid Hops", 5.0, "#A855F7"),
    ]
    widget.set_data(items)
    widget.repaint()
    assert len(widget.items) == 3


def test_overview_page_with_pipeline(qapp):
    overview = OverviewPage()
    overview.resize(1280, 800)
    overview.show()

    # Empty state initially
    assert overview.empty_widget.isVisible()

    # Run lightweight pipeline
    gen = SyntheticBitcoinTrafficGenerator(seed=42)
    records, gt = gen.generate_dataset(num_transactions=30)
    pipeline = InvestigationPipeline()
    res = pipeline.run_investigation(records, ground_truth=gt)
    assert res["status"] == "COMPLETED"

    overview.update_data(pipeline)
    assert not overview.empty_widget.isVisible()
    assert overview.content_scroll.isVisible()

    # Verify chart data populated
    assert len(overview.risk_donut.slices) == 4
    assert len(overview.priority_chart.items) == 4
    assert len(overview.activity_chart.data_points) > 0

    # Theme toggle check
    theme_manager.set_theme("light")
    overview.repaint()
    theme_manager.set_theme("dark")
    overview.repaint()
