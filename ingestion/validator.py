"""Data validation engine for Bitcoin transaction metadata."""
import hashlib
import logging
from typing import Dict, Any, List, Tuple, Set
from core.enums import ValidationStatus
from core.models import TransactionRecord, DataQualityReportData
from core.utils import (
    is_valid_ip,
    is_valid_port,
    is_valid_txid,
    is_valid_bitcoin_address,
    parse_timestamp_iso,
    parse_array_field,
    parse_float_array,
)
from ingestion.normalizer import DataNormalizer

logger = logging.getLogger("TRACE.Validator")


class DataValidator:
    """Validates raw incoming transaction metadata records."""

    def __init__(self):
        self.seen_txids: Set[str] = set()
        self.normalizer = DataNormalizer()

    def reset(self):
        """Reset validation state for new dataset."""
        self.seen_txids.clear()

    def validate_record(self, raw_record: Dict[str, Any]) -> Tuple[ValidationStatus, List[str]]:
        """
        Validate a single raw record.
        Returns (ValidationStatus, List of error/warning strings).
        """
        errors: List[str] = []
        is_quarantine = False

        if not raw_record or not any(raw_record.values()):
            return ValidationStatus.INVALID, ["Empty record"]

        # 1. Resolve TXID (using alias resolution)
        txid_raw = self.normalizer.resolve_field(raw_record, "txid")
        txid_str = str(txid_raw).strip() if txid_raw is not None else ""

        # If no explicit txid, check if we can identify record via other fields
        if not txid_str:
            has_in = self.normalizer.resolve_field(raw_record, "input_addresses")
            has_out = self.normalizer.resolve_field(raw_record, "output_addresses")
            has_time = self.normalizer.resolve_field(raw_record, "timestamp")
            if not has_in and not has_out and not has_time:
                errors.append("Missing required transaction identifiers or addresses")
                return ValidationStatus.INVALID, errors
            seed = f"{id(raw_record)}_{has_time}_{has_in}_{has_out}"
            txid_str = hashlib.sha256(seed.encode("utf-8")).hexdigest()
        elif not is_valid_txid(txid_str):
            # If txid is a short integer or custom string (e.g. '1', '25', 'tx_01'), hash to 64-char hex
            txid_str = hashlib.sha256(f"TX_{txid_str}".encode("utf-8")).hexdigest()

        # Duplicate check
        if txid_str in self.seen_txids:
            errors.append(f"Duplicate TXID detected in dataset: {txid_str}")
            return ValidationStatus.DUPLICATE, errors
        self.seen_txids.add(txid_str)

        # 2. Validate Timestamp
        ts_raw = self.normalizer.resolve_field(raw_record, "timestamp")
        if ts_raw and not str(ts_raw).count(":") and "txn_time" in raw_record:
            ts_raw = f"{ts_raw} {raw_record['txn_time']}"
        ts_obj = parse_timestamp_iso(ts_raw)
        if ts_raw is not None and str(ts_raw).strip() != "" and ts_obj is None:
            errors.append(f"Invalid timestamp format: '{ts_raw}'")
            is_quarantine = True

        # 3. Validate IP addresses (if explicitly provided in dataset)
        src_ip_raw = self.normalizer.resolve_field(raw_record, "src_ip")
        if src_ip_raw is not None and str(src_ip_raw).strip() != "":
            src_ip = str(src_ip_raw).strip()
            if not is_valid_ip(src_ip):
                errors.append(f"Invalid source IP address: '{src_ip}'")
                is_quarantine = True

        dst_ip_raw = self.normalizer.resolve_field(raw_record, "dst_ip")
        if dst_ip_raw is not None and str(dst_ip_raw).strip() != "":
            dst_ip = str(dst_ip_raw).strip()
            if not is_valid_ip(dst_ip):
                errors.append(f"Invalid destination IP address: '{dst_ip}'")
                is_quarantine = True

        # 4. Validate Ports (if explicitly provided in dataset)
        src_port_raw = self.normalizer.resolve_field(raw_record, "src_port")
        if src_port_raw is not None and str(src_port_raw).strip() != "":
            if not is_valid_port(src_port_raw):
                errors.append(f"Invalid source port: '{src_port_raw}' (must be 1-65535)")
                is_quarantine = True

        dst_port_raw = self.normalizer.resolve_field(raw_record, "dst_port")
        if dst_port_raw is not None and str(dst_port_raw).strip() != "":
            if not is_valid_port(dst_port_raw):
                errors.append(f"Invalid destination port: '{dst_port_raw}' (must be 1-65535)")
                is_quarantine = True

        # 5. Validate Amounts (Check negative values)
        in_amounts = parse_float_array(self.normalizer.resolve_field(raw_record, "input_amounts"))
        out_amounts = parse_float_array(self.normalizer.resolve_field(raw_record, "output_amounts"))

        if any(amt < 0 for amt in in_amounts):
            errors.append("Negative value detected in input_amounts")
            return ValidationStatus.INVALID, errors
        if any(amt < 0 for amt in out_amounts):
            errors.append("Negative value detected in output_amounts")
            return ValidationStatus.INVALID, errors

        # 6. Check fee if present
        fee = self.normalizer.resolve_field(raw_record, "fee")
        if fee is not None:
            try:
                f_val = float(fee)
                if f_val < 0:
                    errors.append(f"Negative transaction fee: {f_val}")
                    is_quarantine = True
            except (ValueError, TypeError):
                errors.append(f"Invalid fee format: '{fee}'")
                is_quarantine = True

        if errors:
            status = ValidationStatus.QUARANTINED if is_quarantine else ValidationStatus.INVALID
            return status, errors

        return ValidationStatus.VALID, []
