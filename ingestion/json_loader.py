"""JSON and JSON Lines (JSONL) file loader for Bitcoin transaction metadata."""
import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional, Union

logger = logging.getLogger("TRACE.JSONLoader")


def load_json_data(
    file_path: Union[str, Path],
    max_rows: Optional[int] = None,
) -> Tuple[List[Dict[str, Any]], Optional[str]]:
    """
    Load JSON or JSONL file into list of dictionaries.
    Returns (records, error_string_if_any).
    """
    path = Path(file_path)
    if not path.exists():
        return [], f"File not found: {path}"
    if path.stat().st_size == 0:
        return [], "File is empty (0 bytes)"

    records: List[Dict[str, Any]] = []

    try:
        with open(path, mode="r", encoding="utf-8-sig", errors="replace") as f:
            content = f.read().strip()
            if not content:
                return [], "File contains only whitespace"

            # Case 1: Standard JSON Array or Dict with wrapper key
            if content.startswith("[") or content.startswith("{"):
                try:
                    data = json.loads(content)
                    if isinstance(data, list):
                        records = data if not max_rows else data[:max_rows]
                    elif isinstance(data, dict):
                        # Look for wrapper keys
                        for key in ["transactions", "records", "data", "traffic", "items", "rows"]:
                            if key in data and isinstance(data[key], list):
                                records = data[key] if not max_rows else data[key][:max_rows]
                                break
                        if not records:
                            # Single transaction record in root object
                            records = [data]
                except json.JSONDecodeError:
                    # Could be JSON Lines despite leading brace
                    records = []

            # Case 2: JSON Lines (JSONL)
            if not records:
                lines = content.splitlines()
                for i, line in enumerate(lines):
                    if max_rows and i >= max_rows:
                        break
                    l_str = line.strip()
                    if not l_str:
                        continue
                    try:
                        obj = json.loads(l_str)
                        if isinstance(obj, dict):
                            records.append(obj)
                    except json.JSONDecodeError as jde:
                        return [], f"Malformed JSON on line {i+1}: {jde.msg}"

        if not records:
            return [], "No valid JSON records found in file"

        return records, None

    except Exception as e:
        logger.error(f"Error reading JSON {path}: {e}", exc_info=True)
        return [], f"Failed to parse JSON: {str(e)}"
