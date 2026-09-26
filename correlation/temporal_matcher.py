"""Temporal matching engine for correlating network-blockchain propagation windows."""
from datetime import datetime, timezone
from typing import List, Dict, Any, Tuple
from core.models import TransactionRecord
from core.utils import parse_timestamp_iso


class TemporalMatcher:
    """Matches events occurring in proximate time windows to reconstruct propagation dynamics."""

    def __init__(self, time_window_seconds: int = 120):
        self.time_window_seconds = time_window_seconds

    def find_temporal_clusters(
        self,
        records: List[TransactionRecord],
    ) -> List[List[TransactionRecord]]:
        """Group transactions occurring within the time window into temporal clusters."""
        if not records:
            return []

        # Parse and sort by datetime
        timed_records: List[Tuple[datetime, TransactionRecord]] = []
        for r in records:
            dt = parse_timestamp_iso(r.timestamp)
            if dt:
                timed_records.append((dt, r))

        timed_records.sort(key=lambda x: x[0])

        clusters: List[List[TransactionRecord]] = []
        current_cluster: List[TransactionRecord] = []
        window_start: datetime = None

        for dt, record in timed_records:
            if not current_cluster:
                current_cluster.append(record)
                window_start = dt
            else:
                delta = (dt - window_start).total_seconds()
                if delta <= self.time_window_seconds:
                    current_cluster.append(record)
                else:
                    clusters.append(current_cluster)
                    current_cluster = [record]
                    window_start = dt

        if current_cluster:
            clusters.append(current_cluster)

        return clusters
