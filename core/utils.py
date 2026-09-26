"""Core utility functions for validation, normalization, and hashing."""
import re
import ipaddress
import json
from datetime import datetime, timezone
from typing import List, Any, Union, Optional


HEX64_REGEX = re.compile(r"^[0-9a-fA-F]{64}$")
BTC_ADDR_REGEX = re.compile(r"^(1[a-km-zA-HJ-NP-Z1-9]{25,34}|3[a-km-zA-HJ-NP-Z1-9]{25,34}|bc1[a-z0-9]{11,71}|bcrt1[a-z0-9]{11,71}|tb1[a-z0-9]{11,71})$", re.IGNORECASE)


def is_valid_ip(ip_str: str) -> bool:
    """Validate IPv4 or IPv6 address."""
    if not ip_str or not isinstance(ip_str, str):
        return False
    try:
        ipaddress.ip_address(ip_str.strip())
        return True
    except ValueError:
        return False


def is_valid_port(port: Any) -> bool:
    """Validate port is integer between 1 and 65535."""
    try:
        p = int(port)
        return 1 <= p <= 65535
    except (ValueError, TypeError):
        return False


def is_valid_txid(txid_str: str) -> bool:
    """Validate 64-character hexadecimal TXID."""
    if not txid_str or not isinstance(txid_str, str):
        return False
    return bool(HEX64_REGEX.match(txid_str.strip()))


def is_valid_bitcoin_address(address_str: str) -> bool:
    """Heuristic check for Bitcoin addresses (Legacy 1..., P2SH 3..., Bech32 bc1...)."""
    if not address_str or not isinstance(address_str, str):
        return False
    cleaned = address_str.strip()
    return bool(BTC_ADDR_REGEX.match(cleaned)) or (len(cleaned) >= 26 and len(cleaned) <= 75)


def parse_timestamp_iso(ts_val: Any) -> Optional[datetime]:
    """Parse various timestamp representations into a UTC datetime object."""
    if ts_val is None:
        return None
    if isinstance(ts_val, datetime):
        if ts_val.tzinfo is None:
            return ts_val.replace(tzinfo=timezone.utc)
        return ts_val.astimezone(timezone.utc)
    
    # If float or integer UNIX epoch
    if isinstance(ts_val, (int, float)):
        # Check if ms vs seconds
        if ts_val > 1e11:  # Likely milliseconds
            ts_val = ts_val / 1000.0
        try:
            return datetime.fromtimestamp(ts_val, tz=timezone.utc)
        except (ValueError, OSError):
            return None
            
    # String handling
    ts_str = str(ts_val).strip()
    # Try parsing integer string
    if ts_str.isdigit():
        val = float(ts_str)
        if val > 1e11:
            val = val / 1000.0
        try:
            return datetime.fromtimestamp(val, tz=timezone.utc)
        except (ValueError, OSError):
            pass
            
    # Try standard ISO strings
    for fmt in [
        "%Y-%m-%dT%H:%M:%S%z",
        "%Y-%m-%dT%H:%M:%S.%f%z",
        "%Y-%m-%dT%H:%M:%SZ",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M:%S.%f",
        "%Y/%m/%d %H:%M:%S",
    ]:
        try:
            dt = datetime.strptime(ts_str, fmt)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt.astimezone(timezone.utc)
        except ValueError:
            continue
            
    # Python 3.11+ fromisoformat handles most ISO 8601 variants
    try:
        dt = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)
    except Exception:
        return None


def parse_array_field(val: Any) -> List[Any]:
    """
    Robust array parser: Handles Python list, JSON arrays,
    semicolon-separated, pipe-separated, or comma-separated strings.
    """
    if val is None:
        return []
    if isinstance(val, (list, tuple)):
        return list(val)
    if isinstance(val, str):
        v = val.strip()
        if not v:
            return []
        # JSON array format
        if (v.startswith("[") and v.endswith("]")) or (v.startswith("(") and v.endswith(")")):
            try:
                parsed = json.loads(v.replace("'", '"'))
                if isinstance(parsed, list):
                    return parsed
            except Exception:
                # Strip braces and split
                inner = v[1:-1].strip()
                if not inner:
                    return []
                parts = [x.strip().strip("'\"") for x in inner.split(",") if x.strip()]
                return parts
        # Semicolon separated
        if ";" in v:
            return [x.strip().strip("'\"") for x in v.split(";") if x.strip()]
        # Pipe separated
        if "|" in v:
            return [x.strip().strip("'\"") for x in v.split("|") if x.strip()]
        # Comma separated
        if "," in v:
            return [x.strip().strip("'\"") for x in v.split(",") if x.strip()]
        # Single element
        return [v.strip("'\"")]
    return [val]


def parse_float_array(val: Any) -> List[float]:
    """Parse list of floats with robust fallback."""
    raw_list = parse_array_field(val)
    result = []
    for item in raw_list:
        try:
            result.append(float(item))
        except (ValueError, TypeError):
            result.append(0.0)
    return result
