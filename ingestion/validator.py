"""Data validation engine for Bitcoin transaction metadata."""
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

logger = logging.getLogger("TRACE.Validator")


class DataValidator:
    """Validates raw incoming transaction metadata records."""

    def __init__(self):
        self.seen_txids: Set[str] = set()

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

        # 1. Check required fields presence
        required_fields = ["txid", "timestamp", "src_ip", "dst_ip", "src_port", "dst_port"]
        for rf in required_fields:
            if rf not in raw_record or raw_record[rf] is None or str(raw_record[rf]).strip() == "":
                errors.append(f"Missing required field: '{rf}'")

        if errors:
            return ValidationStatus.INVALID, errors

        # 2. Validate TXID
        txid = str(raw_record.get("txid", "")).strip()
        if not is_valid_txid(txid):
            errors.append(f"Malformed TXID (expected 64-character hex string): '{txid}'")
            return ValidationStatus.INVALID, errors

        # Duplicate check
        if txid in self.seen_txids:
            errors.append(f"Duplicate TXID detected in dataset: {txid}")
            return ValidationStatus.DUPLICATE, errors
        self.seen_txids.add(txid)

        # 3. Validate Timestamp
        ts_obj = parse_timestamp_iso(raw_record.get("timestamp"))
        if ts_obj is None:
            errors.append(f"Invalid timestamp format: '{raw_record.get('timestamp')}'")
            is_quarantine = True

        # 4. Validate IP addresses
        src_ip = str(raw_record.get("src_ip", "")).strip()
        dst_ip = str(raw_record.get("dst_ip", "")).strip()
        if not is_valid_ip(src_ip):
            errors.append(f"Invalid source IP address: '{src_ip}'")
            is_quarantine = True
        if not is_valid_ip(dst_ip):
            errors.append(f"Invalid destination IP address: '{dst_ip}'")
            is_quarantine = True

        # 5. Validate Ports
        src_port = raw_record.get("src_port")
        dst_port = raw_record.get("dst_port")
        if not is_valid_port(src_port):
            errors.append(f"Invalid source port: '{src_port}' (must be 1-65535)")
            is_quarantine = True
        if not is_valid_port(dst_port):
            errors.append(f"Invalid destination port: '{dst_port}' (must be 1-65535)")
            is_quarantine = True

        # 6. Validate Address arrays
        in_addrs = parse_array_field(raw_record.get("input_addresses"))
        out_addrs = parse_array_field(raw_record.get("output_addresses"))
        if not in_addrs:
            errors.append("Empty input_addresses array")
            is_quarantine = True
        if not out_addrs:
            errors.append("Empty output_addresses array")
            is_quarantine = True

        # 7. Validate Amounts
        in_amounts = parse_float_array(raw_record.get("input_amounts"))
        out_amounts = parse_float_array(raw_record.get("output_amounts"))

        # Check negative amounts
        if any(amt < 0 for amt in in_amounts):
            errors.append("Negative value detected in input_amounts")
            return ValidationStatus.INVALID, errors
        if any(amt < 0 for amt in out_amounts):
            errors.append("Negative value detected in output_amounts")
            return ValidationStatus.INVALID, errors

        # Check array lengths mismatch
        if len(in_addrs) != len(in_amounts):
            errors.append(
                f"Array length mismatch: input_addresses has {len(in_addrs)} items but input_amounts has {len(in_amounts)} items"
            )
            is_quarantine = True
        if len(out_addrs) != len(out_amounts):
            errors.append(
                f"Array length mismatch: output_addresses has {len(out_addrs)} items but output_amounts has {len(out_amounts)} items"
            )
            is_quarantine = True

        # Check fee if present
        fee = raw_record.get("fee")
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
