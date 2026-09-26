"""Temporal dynamics and burstiness feature extraction."""
import math
from datetime import datetime
from typing import List, Dict, Any
from core.utils import parse_timestamp_iso


def extract_temporal_features(timestamps_iso: List[str]) -> Dict[str, float]:
    """Compute burstiness, inter-transaction intervals, and velocity metrics."""
    if not timestamps_iso:
        return {
            "tx_velocity_per_hour": 0.0,
            "burst_score": 0.0,
            "avg_interval_seconds": 0.0,
            "std_interval_seconds": 0.0,
            "active_span_hours": 0.0,
        }

    # Parse and sort timestamps
    dts: List[datetime] = []
    for ts in timestamps_iso:
        dt = parse_timestamp_iso(ts)
        if dt:
            dts.append(dt)

    if not dts:
        return {
            "tx_velocity_per_hour": 0.0,
            "burst_score": 0.0,
            "avg_interval_seconds": 0.0,
            "std_interval_seconds": 0.0,
            "active_span_hours": 0.0,
        }

    dts.sort()
    count = len(dts)

    if count == 1:
        return {
            "tx_velocity_per_hour": 1.0,
            "burst_score": 0.0,
            "avg_interval_seconds": 0.0,
            "std_interval_seconds": 0.0,
            "active_span_hours": 0.0,
        }

    span_seconds = max(1.0, (dts[-1] - dts[0]).total_seconds())
    span_hours = span_seconds / 3600.0
    velocity = count / max(0.01, span_hours)

    intervals = [(dts[i + 1] - dts[i]).total_seconds() for i in range(count - 1)]
    avg_interval = sum(intervals) / len(intervals)
    variance = sum((x - avg_interval) ** 2 for x in intervals) / len(intervals)
    std_interval = math.sqrt(variance)

    # Standard burstiness coefficient B = (sigma - mu) / (sigma + mu)
    if (std_interval + avg_interval) > 0:
        burst_score = (std_interval - avg_interval) / (std_interval + avg_interval)
    else:
        burst_score = 0.0

    # Rapid hop detection: count of intervals less than 10 minutes (600 seconds)
    rapid_hop_count = sum(1 for i in intervals if i < 600)

    return {
        "tx_velocity_per_hour": round(velocity, 4),
        "burst_score": round(burst_score, 4),
        "avg_interval_seconds": round(avg_interval, 2),
        "std_interval_seconds": round(std_interval, 2),
        "active_span_hours": round(span_hours, 3),
        "rapid_hop_count": float(rapid_hop_count),
    }
