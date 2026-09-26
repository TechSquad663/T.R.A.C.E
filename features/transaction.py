"""Transaction-level feature extraction."""
from typing import Dict, Any
from core.models import TransactionRecord


def extract_transaction_features(record: TransactionRecord) -> Dict[str, float]:
    """Extract quantitative features from a single TransactionRecord."""
    in_cnt = max(1, record.input_count)
    out_cnt = max(1, record.output_count)
    tot_in = record.total_input_amount
    tot_out = record.total_output_amount

    return {
        "tx_amount": round(tot_out, 6),
        "input_count": float(in_cnt),
        "output_count": float(out_cnt),
        "io_ratio": round(in_cnt / out_cnt, 4),
        "fee": round(record.fee, 6),
        "fee_per_output": round(record.fee / out_cnt, 6),
        "avg_input_amount": round(tot_in / in_cnt, 6),
        "avg_output_amount": round(tot_out / out_cnt, 6),
    }
