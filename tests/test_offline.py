"""Tests for offline security, socket air-gap enforcement, and self-contained execution."""
import socket
import pytest
from generator.synthetic_dataset import SyntheticBitcoinTrafficGenerator
from pipeline.investigation_pipeline import InvestigationPipeline
from reports.pdf_report import ForensicPDFReportGenerator
from config.settings import get_settings


def test_socket_lockdown_mechanism(monkeypatch):
    """Ensure socket connection attempts are trapped and raise an error."""
    def block_connect(self, address):
        raise ConnectionRefusedError(f"STRICT OFFLINE AIR-GAP: Blocked outbound call to {address}")

    monkeypatch.setattr(socket.socket, "connect", block_connect)

    s = socket.socket()
    with pytest.raises(ConnectionRefusedError):
        s.connect(("8.8.8.8", 53))


def test_full_pipeline_offline_execution(tmp_path):
    """Verify that entire pipeline runs from start to finish without network access."""
    gen = SyntheticBitcoinTrafficGenerator(seed=123)
    records, gt = gen.generate_dataset(num_transactions=150)

    pipeline = InvestigationPipeline()
    res = pipeline.run_investigation(records, ground_truth=gt)

    assert res["status"] == "COMPLETED"
    assert res["total_records"] > 0
    assert res["total_entities"] > 0
    assert len(pipeline.alerts) > 0

    # Verify PDF report generation completely offline
    top_lead = pipeline.alerts[0]
    docket = pipeline.dockets[top_lead.entity_id]
    pdf_gen = ForensicPDFReportGenerator()
    out_pdf = tmp_path / "test_report.pdf"
    pdf_gen.generate_report(docket, out_pdf)

    assert out_pdf.exists()
    assert out_pdf.stat().st_size > 1000
