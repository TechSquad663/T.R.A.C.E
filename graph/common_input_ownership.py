"""Common Input Ownership (CIO) heuristic analyzer for graph relationships."""
import logging
from typing import List, Dict, Any, Tuple
import networkx as nx
from core.enums import EdgeType
from core.constants import STATUS_DESCRIPTIONS

logger = logging.getLogger("TRACE.CIOAnalyzer")


class CommonInputAnalyzer:
    """Analyzes co-spending links to evaluate clustering confidence and supporting txs."""

    def __init__(self, graph: nx.MultiDiGraph):
        self.graph = graph

    def find_cio_clusters(self) -> List[Dict[str, Any]]:
        """Extract all connected components formed strictly by COMMON_INPUT edges."""
        cio_subgraph = nx.Graph()

        # Add only COMMON_INPUT edges
        for u, v, data in self.graph.edges(data=True):
            if data.get("edge_type") == EdgeType.COMMON_INPUT.value:
                cio_subgraph.add_edge(u, v, **data)

        clusters = []
        for idx, component in enumerate(nx.connected_components(cio_subgraph)):
            members = list(component)
            supporting_tx_count = sum(
                data.get("co_spending_count", 1)
                for u, v, data in cio_subgraph.subgraph(component).edges(data=True)
            )
            clusters.append({
                "cluster_index": idx + 1,
                "member_wallets": members,
                "wallet_count": len(members),
                "supporting_tx_count": supporting_tx_count,
                "heuristic_confidence": min(0.95, 0.70 + (supporting_tx_count * 0.05)),
                "forensic_label": STATUS_DESCRIPTIONS["CIO_HEURISTIC"],
            })

        return clusters
