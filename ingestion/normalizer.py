"""Data normalization engine converting raw records to canonical TransactionRecords."""
import hashlib
import logging
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from core.enums import ValidationStatus
from core.models import TransactionRecord
from core.utils import (
    parse_timestamp_iso,
    parse_array_field,
    parse_float_array,
    is_valid_ip,
    is_valid_port,
)

logger = logging.getLogger("TRACE.Normalizer")

DEFAULT_FIELD_ALIASES = {
    "src_ip": ["src_ip", "source_ip", "source_address", "src", "client_ip", "peer_ip", "ip", "host"],
    "dst_ip": ["dst_ip", "dest_ip", "destination_ip", "destination_address", "dst", "node_ip", "target_ip", "server_ip"],
    "src_port": ["src_port", "source_port", "sport", "s_port"],
    "dst_port": ["dst_port", "dest_port", "destination_port", "dport", "d_port"],
    "txid": ["txid", "tx_hash", "transaction_hash", "tx_id", "txn_id", "hash", "trans_num", "id"],
    "timestamp": ["timestamp", "txn_time", "time", "date", "observed_at", "ts", "block_time", "txn_date", "block_date"],
    "input_addresses": ["input_addresses", "inputs", "input", "vin_addresses", "from_addresses", "senders", "vin", "from", "member_id", "sender", "source_address", "address"],
    "output_addresses": ["output_addresses", "outputs", "output", "vout_addresses", "to_addresses", "receivers", "vout", "to", "recipient", "dest_address", "destination_address"],
    "input_amounts": ["input_amounts", "vin_amounts", "input_values", "values_in", "amounts_in", "quantity", "amount", "sum"],
    "output_amounts": ["output_amounts", "vout_amounts", "output_values", "values_out", "amounts_out", "sum", "quantity", "amount", "value", "total_btc_per_block"],
    "fee": ["fee", "tx_fee", "fees", "mining_fee", "percentage_fee"],
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
        norm_notes = list(notes or [])

        # 1. Resolve & Canonicalize TXID (must be valid 64-char hex)
        txid_raw = self.resolve_field(raw_record, "txid")
        txid = str(txid_raw).strip() if txid_raw is not None else ""
        if not txid or len(txid) != 64 or not all(c in "0123456789abcdefABCDEF" for c in txid):
            seed_parts = [
                str(txid_raw or ""),
                str(self.resolve_field(raw_record, "timestamp") or ""),
                str(self.resolve_field(raw_record, "input_addresses") or ""),
                str(self.resolve_field(raw_record, "output_addresses") or ""),
                str(self.resolve_field(raw_record, "output_amounts") or ""),
                str(id(raw_record)),
            ]
            txid = hashlib.sha256("_".join(seed_parts).encode("utf-8")).hexdigest()

        # 2. Resolve Timestamp
        ts_raw = self.resolve_field(raw_record, "timestamp")
        # Handle split date and time columns safely
        if ts_raw and not str(ts_raw).count(":") and "txn_time" in raw_record:
            time_part = str(raw_record["txn_time"]).strip()
            if ":" in time_part and not "-" in time_part:
                ts_raw = f"{ts_raw} {time_part}"
            elif ":" in time_part and "-" in time_part:
                ts_raw = time_part
        ts_obj = parse_timestamp_iso(ts_raw)
        if ts_obj:
            timestamp_str = ts_obj.isoformat()
        elif ts_raw:
            timestamp_str = str(ts_raw)
        else:
            timestamp_str = datetime.now(timezone.utc).isoformat()

        # 3. Resolve Input & Output Addresses
        raw_inputs = parse_array_field(self.resolve_field(raw_record, "input_addresses"))
        raw_outputs = parse_array_field(self.resolve_field(raw_record, "output_addresses"))
        input_amounts = parse_float_array(self.resolve_field(raw_record, "input_amounts"))
        output_amounts = parse_float_array(self.resolve_field(raw_record, "output_amounts"))

        # Clean addresses and extract any interleaved numeric amounts (e.g., summarised_data.csv format)
        clean_in_addrs = []
        for item in raw_inputs:
            s = str(item).strip()
            try:
                float(s)
            except ValueError:
                if s:
                    clean_in_addrs.append(s)

        clean_out_addrs = []
        extracted_out_amts = []
        for item in raw_outputs:
            s = str(item).strip()
            try:
                amt_val = float(s)
                extracted_out_amts.append(amt_val)
            except ValueError:
                if s:
                    clean_out_addrs.append(s)

        input_addresses = clean_in_addrs
        output_addresses = clean_out_addrs

        if not output_amounts and extracted_out_amts:
            output_amounts = extracted_out_amts

        # Fallback addresses if dataset only provides member/wallet references
        if not input_addresses:
            mid = self.resolve_field(raw_record, "member_id")
            if mid:
                input_addresses = [f"WAL_{mid}"]
            else:
                input_addresses = [f"ADDR_IN_{txid[:10]}"]

        if not output_addresses:
            output_addresses = [f"ADDR_OUT_{txid[-10:]}"]

        # Amount fallbacks
        if not output_amounts:
            output_amounts = [sum(input_amounts)] if input_amounts else [1.0]
        if not input_amounts:
            input_amounts = [sum(output_amounts)] if output_amounts else [1.0]

        # 4. Resolve P2P Network Telemetry (Synthesize gracefully for pure on-chain datasets)
        src_ip = str(self.resolve_field(raw_record, "src_ip") or "").strip()
        dst_ip = str(self.resolve_field(raw_record, "dst_ip") or "").strip()

        if not src_ip or not is_valid_ip(src_ip):
            addr_seed = input_addresses[0] if input_addresses else txid
            h = abs(hash(str(addr_seed)))
            src_ip = f"10.{(h >> 16) % 254 + 1}.{(h >> 8) % 254 + 1}.{(h & 0xFF) % 254 + 1}"
            norm_notes.append("P2P network layer synthesized for on-chain metadata")

        if not dst_ip or not is_valid_ip(dst_ip):
            dst_ip = "198.51.100.1"

        try:
            src_port = int(self.resolve_field(raw_record, "src_port") or 8333)
        except (ValueError, TypeError):
            src_port = 8333
        if not is_valid_port(src_port):
            src_port = 8333

        try:
            dst_port = int(self.resolve_field(raw_record, "dst_port") or 8333)
        except (ValueError, TypeError):
            dst_port = 8333
        if not is_valid_port(dst_port):
            dst_port = 8333

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
            validation_notes=norm_notes,
        )
