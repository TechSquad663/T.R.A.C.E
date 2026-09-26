"""Tests for network-blockchain correlation and entity resolution."""
import pytest
from core.models import TransactionRecord
from correlation.network_blockchain import NetworkBlockchainCorrelator
from correlation.entity_resolution import EntityResolver, DisjointSetUnion


def test_disjoint_set_union():
    dsu = DisjointSetUnion()
    dsu.union("addrA", "addrB")
    dsu.union("addrB", "addrC")
    assert dsu.find("addrA") == dsu.find("addrC")
    assert dsu.find("addrA") != dsu.find("addrX")


def test_cio_entity_resolution():
    records = [
        TransactionRecord(
            txid="1" * 64,
            timestamp="2026-03-01T10:00:00Z",
            src_ip="192.168.1.1",
            dst_ip="10.0.0.1",
            src_port=8333,
            dst_port=8333,
            input_addresses=["walletA", "walletB"],  # Co-spent
            output_addresses=["walletC"],
            input_amounts=[1.0, 1.0],
            output_amounts=[1.99],
        ),
        TransactionRecord(
            txid="2" * 64,
            timestamp="2026-03-01T10:05:00Z",
            src_ip="192.168.1.1",
            dst_ip="10.0.0.1",
            src_port=8333,
            dst_port=8333,
            input_addresses=["walletB", "walletD"],  # Co-spent with B
            output_addresses=["walletE"],
            input_amounts=[1.0, 2.0],
            output_amounts=[2.99],
        ),
    ]

    resolver = EntityResolver()
    entities = resolver.resolve_entities(records)

    # Wallets A, B, D should belong to the same resolved entity
    ent_a = resolver.get_entity_id_for_address("walletA")
    ent_b = resolver.get_entity_id_for_address("walletB")
    ent_d = resolver.get_entity_id_for_address("walletD")

    assert ent_a == ent_b
    assert ent_b == ent_d
    assert "ENT_CIO_" in ent_a

    # Check relationships
    cio_links = resolver.get_cio_relationships()
    assert len(cio_links) >= 2


def test_network_blockchain_correlation():
    records = [
        TransactionRecord(
            txid="a" * 64,
            timestamp="2026-03-01T10:00:00Z",
            src_ip="45.33.32.1",
            dst_ip="10.0.0.1",
            src_port=8333,
            dst_port=8333,
            input_addresses=["w1"],
            output_addresses=["w2"],
            input_amounts=[1.0],
            output_amounts=[0.99],
        )
    ]
    correlator = NetworkBlockchainCorrelator()
    res = correlator.correlate(records)

    assert res["total_correlated_transactions"] == 1
    assert "w1" in correlator.get_wallets_for_ip("45.33.32.1")
    assert "w2" in correlator.get_wallets_for_ip("45.33.32.1")
    assert "45.33.32.1" in correlator.get_ips_for_wallet("w1")
