"""Tests for NetworkX graph construction and topological analysis."""
import pytest
from core.models import TransactionRecord
from graph.graph_builder import GraphBuilder
from graph.graph_features import GraphFeatureExtractor
from graph.path_analysis import PathAnalyzer


def test_graph_builder_and_features():
    records = [
        TransactionRecord(
            txid="1" * 64,
            timestamp="2026-03-01T10:00:00Z",
            src_ip="192.168.1.1",
            dst_ip="10.0.0.1",
            src_port=8333,
            dst_port=8333,
            input_addresses=["wallet1"],
            output_addresses=["wallet2", "wallet3"],
            input_amounts=[5.0],
            output_amounts=[2.0, 2.999],
            fee=0.001,
        )
    ]

    builder = GraphBuilder()
    g = builder.build_graph(records)

    assert g.number_of_nodes() >= 4  # IP, TX, 3 Wallets
    assert g.number_of_edges() >= 3  # OBSERVED, INPUT, 2 OUTPUT

    extractor = GraphFeatureExtractor(g)
    metrics = extractor.compute_all_metrics()

    w1_key = "WAL_wallet1"
    assert w1_key in metrics
    assert metrics[w1_key]["out_degree"] >= 1.0


def test_path_analyzer_evidence_chain():
    records = [
        TransactionRecord(
            txid="1" * 64,
            timestamp="2026-03-01T10:00:00Z",
            src_ip="192.168.1.1",
            dst_ip="10.0.0.1",
            src_port=8333,
            dst_port=8333,
            input_addresses=["walletA"],
            output_addresses=["walletB"],
            input_amounts=[2.0],
            output_amounts=[1.999],
        ),
        TransactionRecord(
            txid="2" * 64,
            timestamp="2026-03-01T10:02:00Z",
            src_ip="192.168.1.2",
            dst_ip="10.0.0.1",
            src_port=8333,
            dst_port=8333,
            input_addresses=["walletB"],
            output_addresses=["walletC"],
            input_amounts=[1.999],
            output_amounts=[1.998],
        ),
    ]

    builder = GraphBuilder()
    g = builder.build_graph(records)
    analyzer = PathAnalyzer(g)

    path = analyzer.find_shortest_evidence_path("WAL_walletA", "WAL_walletC")
    assert path is not None
    assert len(path) >= 3

    chain = analyzer.build_evidence_chain(path)
    assert len(chain) == len(path) - 1
    assert "relationship" in chain[0]
