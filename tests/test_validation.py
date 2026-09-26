"""Tests for data validation and normalization logic."""
import pytest
from core.enums import ValidationStatus
from ingestion.validator import DataValidator
from ingestion.normalizer import DataNormalizer


@pytest.fixture
def validator():
    return DataValidator()


@pytest.fixture
def normalizer():
    return DataNormalizer()


def test_validator_valid_record(validator):
    rec = {
        "txid": "a" * 64,
        "timestamp": "2026-03-01T10:00:00Z",
        "src_ip": "192.168.1.10",
        "dst_ip": "10.0.0.1",
        "src_port": 8333,
        "dst_port": 8333,
        "input_addresses": ["bc1qw508d6qejxtdg4y5r3zarvary0c5xw7kv8f3t4"],
        "output_addresses": ["1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa"],
        "input_amounts": [1.5],
        "output_amounts": [1.4998],
    }
    status, errors = validator.validate_record(rec)
    assert status == ValidationStatus.VALID
    assert len(errors) == 0


def test_validator_duplicate_txid(validator):
    rec = {
        "txid": "b" * 64,
        "timestamp": "2026-03-01T10:00:00Z",
        "src_ip": "1.1.1.1",
        "dst_ip": "2.2.2.2",
        "src_port": 8333,
        "dst_port": 8333,
        "input_addresses": ["addr1"],
        "output_addresses": ["addr2"],
        "input_amounts": [1.0],
        "output_amounts": [0.99],
    }
    status1, _ = validator.validate_record(rec)
    status2, errors2 = validator.validate_record(rec)
    assert status1 == ValidationStatus.VALID
    assert status2 == ValidationStatus.DUPLICATE
    assert "Duplicate TXID" in errors2[0]


def test_validator_invalid_ip(validator):
    rec = {
        "txid": "c" * 64,
        "timestamp": "2026-03-01T10:00:00Z",
        "src_ip": "not_an_ip_address",
        "dst_ip": "10.0.0.1",
        "src_port": 8333,
        "dst_port": 8333,
        "input_addresses": ["addr1"],
        "output_addresses": ["addr2"],
        "input_amounts": [1.0],
        "output_amounts": [0.99],
    }
    status, errors = validator.validate_record(rec)
    assert status == ValidationStatus.QUARANTINED
    assert any("Invalid source IP" in e for e in errors)


def test_validator_negative_amount(validator):
    rec = {
        "txid": "d" * 64,
        "timestamp": "2026-03-01T10:00:00Z",
        "src_ip": "1.1.1.1",
        "dst_ip": "2.2.2.2",
        "src_port": 8333,
        "dst_port": 8333,
        "input_addresses": ["addr1"],
        "output_addresses": ["addr2"],
        "input_amounts": [-5.0],
        "output_amounts": [0.99],
    }
    status, errors = validator.validate_record(rec)
    assert status == ValidationStatus.INVALID
    assert any("Negative value" in e for e in errors)


def test_normalizer_array_parsing(normalizer):
    rec = {
        "txid": "e" * 64,
        "timestamp": "2026-03-01T10:00:00Z",
        "src_ip": "1.1.1.1",
        "dst_ip": "2.2.2.2",
        "src_port": "8333",
        "dst_port": 8333,
        "input_addresses": "addr1;addr2",  # Semicolon separated
        "output_addresses": "['out1', 'out2']",  # JSON array string
        "input_amounts": "1.0;2.0",
        "output_amounts": "[1.5, 1.499]",
    }
    tx_rec = normalizer.normalize_record(rec)
    assert len(tx_rec.input_addresses) == 2
    assert len(tx_rec.output_addresses) == 2
    assert tx_rec.total_input_amount == 3.0
    assert round(tx_rec.total_output_amount, 3) == 2.999
    assert tx_rec.src_port == 8333
