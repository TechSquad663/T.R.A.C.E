"""Data normalization engine converting raw records to canonical TransactionRecords."""
import logging
from typing import Dict, Any, List, Optional
from core.enums import ValidationStatus
from core.models import TransactionRecord
from core.utils import (
    parse_timestamp_iso,
    parse_array_field,
    parse_float_array,
)

logger = logging.getLogger("TRACE.Normalizer")

DEFAULT_FIELD_ALIASES = {
    "src_ip": ["src_ip", "source_ip", "source_address", "src", "client_ip", "peer_ip"],
    "dst_ip": ["dst_ip", "dest_ip", "destination_ip", "destination_address", "dst", "node_ip"],
    "src_port": ["src_port", "source_port", "sport", "s_port"],
    "dst_port": ["dst_port", "dest_port", "destination_port", "dport", "d_port"],
    "txid": ["txid", "tx_hash", "transaction_hash", "tx_id", "hash"],
    "timestamp": ["timestamp", "time", "date", "observed_at", "ts", "block_time"],
    "input_addresses": ["input_addresses", "inputs", "vin_addresses", "from_addresses", "senders", "vin"],
    "output_addresses": ["output_addresses", "outputs", "vout_addresses", "to_addresses", "receivers", "vout"],
    "input_amounts": ["input_amounts", "vin_amounts", "input_values", "values_in", "amounts_in"],
    "output_amounts": ["output_amounts", "vout_amounts", "output_values", "values_out", "amounts_out"],
    "fee": ["fee", "tx_fee", "fees", "mining_fee"],
    "script_type": ["script_type", "type", "tx_type", "address_type"],
    "geo_country": ["geo_country", "country", "src_country", "country_code", "geo"],
    "asn": ["asn", "as_number", "autonomous_system", "src_asn"],
}


class DataNormalizer:
    """Normalizes raw input dictionaries into canonical TransactionRecord instances."""

    def __init__(self, custom_mapping: Optional[Dict[str, str]] = None):
        """
        custom_mapping: map canonical_name -> external_name
        """
        self.custom_mapping = custom_mapping or {}

    def resolve_field(self, raw_record: Dict[str, Any], canonical_name: str) -> Any:
        """Resolve the value for a canonical field using custom mapping or common aliases."""
        # 1. Custom explicit mapping
        if canonical_name in self.custom_mapping:
            ext_key = self.custom_mapping[canonical_name]
            if ext_key in raw_record:
                return raw_record[ext_key]

        # 2. Direct match
        if canonical_name in raw_record:
            return raw_record[canonical_name]

        # 3. Common aliases (case-insensitive)
        aliases = DEFAULT_FIELD_ALIASES.get(canonical_name, [])
        record_keys_lower = {k.lower(): k for k in raw_record.keys()}
        for alias in aliases:
            if alias.lower() in record_keys_lower:
                return raw_record[record_keys_lower[alias.lower()]]

        return None

    def normalize_record(
        self,
        raw_record: Dict[str, Any],
        status: ValidationStatus = ValidationStatus.VALID,
        notes: Optional[List[str]] = None,
    ) -> TransactionRecord:
        """Construct a validated and standardized TransactionRecord."""
        txid_raw = self.resolve_field(raw_record, "txid")
        txid = str(txid_raw).strip() if txid_raw else ""

        ts_raw = self.resolve_field(raw_record, "timestamp")
        ts_obj = parse_timestamp_iso(ts_raw)
        timestamp_str = ts_obj.isoformat() if ts_obj else (str(ts_raw) if ts_raw else "")

        src_ip = str(self.resolve_field(raw_record, "src_ip") or "").strip()
        dst_ip = str(self.resolve_field(raw_record, "dst_ip") or "").strip()

        try:
            src_port = int(self.resolve_field(raw_record, "src_port") or 8333)
        except (ValueError, TypeError):
            src_port = 8333

        try:
            dst_port = int(self.resolve_field(raw_record, "dst_port") or 8333)
        except (ValueError, TypeError):
            dst_port = 8333

        input_addresses = parse_array_field(self.resolve_field(raw_record, "input_addresses"))
        output_addresses = parse_array_field(self.resolve_field(raw_record, "output_addresses"))
        input_amounts = parse_float_array(self.resolve_field(raw_record, "input_amounts"))
        output_amounts = parse_float_array(self.resolve_field(raw_record, "output_amounts"))

        # Fee calculation
        fee_raw = self.resolve_field(raw_record, "fee")
        if fee_raw is not None:
            try:
                fee = float(fee_raw)
            except (ValueError, TypeError):
                fee = 0.0
        else:
            tot_in = sum(input_amounts)
            tot_out = sum(output_amounts)
            fee = max(0.0, round(tot_in - tot_out, 8)) if (tot_in > tot_out and tot_out > 0) else 0.0001

        script_type = str(self.resolve_field(raw_record, "script_type") or "P2PKH").strip()
        geo_country = str(self.resolve_field(raw_record, "geo_country") or "Unknown").strip()
        asn = str(self.resolve_field(raw_record, "asn") or "Unknown").strip()

        return TransactionRecord(
            txid=txid,
            timestamp=timestamp_str,
            src_ip=src_ip,
            dst_ip=dst_ip,
            src_port=src_port,
            dst_port=dst_port,
            input_addresses=[str(a).strip() for a in input_addresses if str(a).strip()],
            output_addresses=[str(a).strip() for a in output_addresses if str(a).strip()],
            input_amounts=input_amounts,
            output_amounts=output_amounts,
            fee=fee,
            script_type=script_type,
            geo_country=geo_country,
            asn=asn,
            validation_status=status,
            validation_notes=notes or [],
        )
