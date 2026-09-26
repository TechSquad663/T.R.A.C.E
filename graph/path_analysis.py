"""Path analysis and evidence chain generation across network and blockchain layers."""
import logging
import networkx as nx
from typing import List, Dict, Any, Optional

logger = logging.getLogger("TRACE.PathAnalysis")


class PathAnalyzer:
    """Computes shortest paths, k-hop neighborhoods, and converts walks to forensic evidence chains."""

    def __init__(self, graph: nx.MultiDiGraph):
        self.graph = graph
        self.undirected_view = nx.Graph(graph)

    def extract_neighborhood(self, root_node: str, hops: int = 1) -> nx.MultiDiGraph:
        """Extract k-hop ego subgraph centered around root_node."""
        if not self.graph.has_node(root_node):
            return nx.MultiDiGraph()

        # Find nodes within k hops
        lengths = nx.single_source_shortest_path_length(self.undirected_view, root_node, cutoff=hops)
        sub_nodes = set(lengths.keys())

        # Return induced subgraph
        subgraph = self.graph.subgraph(sub_nodes).copy()
        return subgraph

    def find_shortest_evidence_path(self, source: str, target: str) -> Optional[List[str]]:
        """Compute shortest path between two nodes in undirected projection."""
        if not self.graph.has_node(source) or not self.graph.has_node(target):
            return None
        try:
            path = nx.shortest_path(self.undirected_view, source=source, target=target)
            return path
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            return None

    def build_evidence_chain(self, path_nodes: List[str]) -> List[Dict[str, Any]]:
        """
        Convert a sequence of node IDs into a structured evidentiary chain:
        e.g., IP_A -> OBSERVED -> TX_102 -> OUTPUT -> WALLET_B -> INPUT -> TX_205 -> OUTPUT -> WALLET_C
        """
        if not path_nodes or len(path_nodes) < 2:
            return []

        chain = []
        for i in range(len(path_nodes) - 1):
            u = path_nodes[i]
            v = path_nodes[i + 1]

            u_data = self.graph.nodes.get(u, {})
            v_data = self.graph.nodes.get(v, {})

            # Inspect edge attributes
            edge_data = None
            if self.graph.has_edge(u, v):
                edge_dict = self.graph.get_edge_data(u, v)
                edge_data = list(edge_dict.values())[0] if edge_dict else {}
            elif self.graph.has_edge(v, u):
                edge_dict = self.graph.get_edge_data(v, u)
                edge_data = list(edge_dict.values())[0] if edge_dict else {}

            edge_type = edge_data.get("edge_type", "ASSOCIATED") if edge_data else "LINKED"
            confidence = edge_data.get("confidence", 0.85) if edge_data else 0.85

            step = {
                "step_number": i + 1,
                "from_node": u,
                "from_type": u_data.get("node_type", "Unknown"),
                "from_label": u_data.get("label", u),
                "relationship": edge_type,
                "to_node": v,
                "to_type": v_data.get("node_type", "Unknown"),
                "to_label": v_data.get("label", v),
                "confidence": confidence,
                "evidence_summary": f"{u_data.get('node_type', '')} [{u}] {edge_type} -> {v_data.get('node_type', '')} [{v}]",
            }
            chain.append(step)

        return chain
