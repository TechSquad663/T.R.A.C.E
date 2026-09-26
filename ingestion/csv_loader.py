"""CSV file loader with automatic delimiter detection and chunked stream parsing."""
import csv
import io
import logging
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional, Union

logger = logging.getLogger("TRACE.CSVLoader")


def detect_delimiter(sample_text: str) -> str:
    """Detect CSV delimiter from sample text."""
    delimiters = [",", "\t", ";", "|"]
    counts = {d: sample_text.count(d) for d in delimiters}
    # Pick the delimiter with highest occurrence
    best = max(counts, key=counts.get)
    return best if counts[best] > 0 else ","


def load_csv_data(
    file_path: Union[str, Path],
    max_rows: Optional[int] = None,
) -> Tuple[List[Dict[str, Any]], Optional[str]]:
    """
    Load CSV data into list of raw dictionaries.
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
            # Read sample for dialect sniffing
            sample = f.read(8192)
            if not sample.strip():
                return [], "File contains only whitespace"
            f.seek(0)

            delimiter = detect_delimiter(sample)
            reader = csv.DictReader(f, delimiter=delimiter)

            if reader.fieldnames is None or not any(reader.fieldnames):
                return [], "CSV has no headers / column names"

            for i, row in enumerate(reader):
                if max_rows and i >= max_rows:
                    break
                # Filter out None keys if line had extra fields
                cleaned_row = {
                    (str(k).strip() if k else f"col_{idx}"): (v.strip() if isinstance(v, str) else v)
                    for idx, (k, v) in enumerate(row.items())
                    if k is not None
                }
                records.append(cleaned_row)

        if not records:
            return [], "CSV contains header only, no records found"

        return records, None
    except Exception as e:
        logger.error(f"Error reading CSV {path}: {e}", exc_info=True)
        return [], f"Failed to parse CSV: {str(e)}"
