"""Unified feature pipeline transforming raw transactions and graph state into ML feature matrices."""
import logging
import pandas as pd
import numpy as np
from typing import List, Dict, Any, Tuple, Optional
from core.models import TransactionRecord, Entity
from .behavioral import extract_wallet_behavioral_features
from .temporal import extract_temporal_features
from .network import extract_network_features
from .graph import extract_entity_graph_features

logger = logging.getLogger("TRACE.FeaturePipeline")

FEATURE_COLUMNS = [
    # Behavioral
    "tx_count",
    "total_in",
    "total_out",
    "avg_amount",
    "max_amount",
    "std_amount",
    "unique_counterparties",
    "fan_in_ratio",
    "fan_out_ratio",
    "peeling_chain_count",
    # Temporal
    "tx_velocity_per_hour",
    "burst_score",
    "avg_interval_seconds",
    "std_interval_seconds",
    "active_span_hours",
    "rapid_hop_count",
    # Network
    "unique_source_ips",
    "unique_dest_ips",
    "unique_countries",
    "unique_asns",
    "ip_reuse_rate",
    "port_diversity",
    # Graph
    "graph_degree",
    "graph_in_degree",
    "graph_out_degree",
    "graph_fan_in_ratio",
    "graph_fan_out_ratio",
    "graph_pagerank",
    "graph_betweenness",
    "graph_clustering_coeff",
    "graph_component_size",
]


class FeaturePipeline:
    """Orchestrates entity feature vector generation for machine learning."""

    def __init__(self):
        self.feature_columns = list(FEATURE_COLUMNS)

    def extract_features_for_entities(
        self,
        entities: Dict[str, Entity],
        records: List[TransactionRecord],
        graph_metrics: Dict[str, Dict[str, float]],
    ) -> pd.DataFrame:
        """
        Build feature matrix indexed by entity_id.
        STRICT COMPLIANCE: No synthetic scenario labels or ground truth allowed.
        """
        # Index records by address and txid for fast lookup
        addr_to_records: Dict[str, List[TransactionRecord]] = {}
        for r in records:
            for a in r.input_addresses + r.output_addresses:
                addr_to_records.setdefault(a, []).append(r)

        rows = []
        entity_ids = []

        for ent_id, entity in entities.items():
            # Collect all transactions associated with this entity's addresses
            ent_records_set = {}
            for a in entity.addresses:
                for r in addr_to_records.get(a, []):
                    ent_records_set[r.txid] = r
            ent_records = list(ent_records_set.values())

            # 1. Behavioral
            b_feat = extract_wallet_behavioral_features(entity.addresses, ent_records)

            # 2. Temporal
            timestamps = [r.timestamp for r in ent_records if r.timestamp]
            t_feat = extract_temporal_features(timestamps)

            # 3. Network
            obs = [
                {
                    "src_ip": r.src_ip,
                    "dst_ip": r.dst_ip,
                    "src_port": r.src_port,
                    "geo_country": r.geo_country,
                    "asn": r.asn,
                }
                for r in ent_records
            ]
            n_feat = extract_network_features(obs)

            # 4. Graph
            node_key = f"WAL_{entity.addresses[0][:14]}" if entity.addresses else f"ENT_{ent_id}"
            g_feat = extract_entity_graph_features(node_key, graph_metrics)

            # Combine into single feature dict
            row = {}
            row.update(b_feat)
            row.update(t_feat)
            row.update(n_feat)
            row.update(g_feat)

            # Keep only allowed columns in order
            ordered_row = {col: float(row.get(col, 0.0)) for col in self.feature_columns}
            rows.append(ordered_row)
            entity_ids.append(ent_id)

        df = pd.DataFrame(rows, index=entity_ids, columns=self.feature_columns)
        df.fillna(0.0, inplace=True)
        return df
