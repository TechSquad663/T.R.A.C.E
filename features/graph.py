"""Entity-level graph feature mapping."""
from typing import Dict, Any


def extract_entity_graph_features(
    node_id: str,
    graph_metrics: Dict[str, Dict[str, float]],
) -> Dict[str, float]:
    """Retrieve graph topological features for an entity or wallet node."""
    metrics = graph_metrics.get(node_id, {})
    return {
        "graph_degree": float(metrics.get("degree", 0.0)),
        "graph_in_degree": float(metrics.get("in_degree", 0.0)),
        "graph_out_degree": float(metrics.get("out_degree", 0.0)),
        "graph_fan_in_ratio": float(metrics.get("fan_in_ratio", 0.0)),
        "graph_fan_out_ratio": float(metrics.get("fan_out_ratio", 0.0)),
        "graph_pagerank": float(metrics.get("pagerank", 0.0)),
        "graph_betweenness": float(metrics.get("betweenness", 0.0)),
        "graph_clustering_coeff": float(metrics.get("clustering_coefficient", 0.0)),
        "graph_component_size": float(metrics.get("component_size", 1.0)),
    }
