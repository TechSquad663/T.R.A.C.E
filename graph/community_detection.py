"""Community detection engine for discovering behavioral clusters."""
import logging
import networkx as nx
from typing import Dict, List, Any

logger = logging.getLogger("TRACE.CommunityDetector")


class CommunityDetector:
    """Discovers transactional communities using modularity optimization and connected components."""

    def __init__(self, graph: nx.MultiDiGraph):
        self.graph = graph
        self.undirected_view = nx.Graph(graph)

    def detect_communities(self) -> Dict[str, int]:
        """Assign community/cluster IDs to each node in the graph."""
        if len(self.undirected_view) == 0:
            return {}

        node_to_community: Dict[str, int] = {}
        try:
            # Try Clauset-Newman-Moore greedy modularity maximization
            communities = list(nx.community.greedy_modularity_communities(self.undirected_view))
            for cid, comm in enumerate(communities):
                for node in comm:
                    node_to_community[node] = cid
        except Exception as e:
            logger.warning(f"Modularity clustering fallback to connected components: {e}")
            for cid, comp in enumerate(nx.connected_components(self.undirected_view)):
                for node in comp:
                    node_to_community[node] = cid

        return node_to_community
