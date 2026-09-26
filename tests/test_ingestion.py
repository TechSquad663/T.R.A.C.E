"""Tests for CSV, JSON, and XML ingestion loaders."""
import pytest
from pathlib import Path
import json
from ingestion.csv_loader import load_csv_data, detect_delimiter
from ingestion.json_loader import load_json_data
from ingestion.xml_loader import load_xml_data


def test_detect_delimiter():
    assert detect_delimiter("col1,col2,col3") == ","
    assert detect_delimiter("col1;col2;col3") == ";"
    assert detect_delimiter("col1\tcol2\tcol3") == "\t"


def test_csv_loader_valid(tmp_path):
    csv_file = tmp_path / "valid.csv"
    csv_file.write_text("txid,src_ip,dst_ip,timestamp\nabc,1.1.1.1,2.2.2.2,2026-03-01T10:00:00Z\n", encoding="utf-8")
    records, err = load_csv_data(csv_file)
    assert err is None
    assert len(records) == 1
    assert records[0]["txid"] == "abc"


def test_csv_loader_empty(tmp_path):
    empty_file = tmp_path / "empty.csv"
    empty_file.write_text("", encoding="utf-8")
    records, err = load_csv_data(empty_file)
    assert len(records) == 0
    assert err is not None


def test_json_loader_valid(tmp_path):
    json_file = tmp_path / "valid.json"
    data = [{"txid": "abc1234", "src_ip": "1.1.1.1", "dst_ip": "2.2.2.2"}]
    json_file.write_text(json.dumps(data), encoding="utf-8")
    records, err = load_json_data(json_file)
    assert err is None
    assert len(records) == 1
    assert records[0]["txid"] == "abc1234"


def test_json_loader_malformed(tmp_path):
    bad_json = tmp_path / "bad.json"
    bad_json.write_text("{\"txid\": bad_unquoted_value}", encoding="utf-8")
    records, err = load_json_data(bad_json)
    assert len(records) == 0
    assert err is not None


def test_xml_loader_valid(tmp_path):
    xml_file = tmp_path / "valid.xml"
    content = """<?xml version="1.0"?>
    <transactions>
        <transaction>
            <txid>hash123</txid>
            <src_ip>10.0.0.1</src_ip>
            <dst_ip>10.0.0.2</dst_ip>
        </transaction>
    </transactions>
    """
    xml_file.write_text(content, encoding="utf-8")
    records, err = load_xml_data(xml_file)
    assert err is None
    assert len(records) == 1
    assert records[0]["txid"] == "hash123"


def test_xml_loader_malformed(tmp_path):
    bad_xml = tmp_path / "bad.xml"
    bad_xml.write_text("<transactions><unclosed_tag>", encoding="utf-8")
    records, err = load_xml_data(bad_xml)
    assert len(records) == 0
    assert err is not None
