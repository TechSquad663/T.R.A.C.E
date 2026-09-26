"""Graph topological and centrality feature extraction engine."""
import logging
import networkx as nx
from typing import Dict, Any

logger = logging.getLogger("TRACE.GraphFeatures")


class GraphFeatureExtractor:
    """Extracts graph topological and centrality metrics for behavioral modeling."""

    def __init__(self, graph: nx.MultiDiGraph):
        self.graph = graph
        # Create simple DiGraph for standard centrality algorithms
        self.simple_digraph = nx.DiGraph(graph)
        self.simple_undirected = self.simple_digraph.to_undirected()

    def compute_all_metrics(self) -> Dict[str, Dict[str, float]]:
        """Compute metrics for all nodes in the graph."""
        metrics: Dict[str, Dict[str, float]] = {}

        if self.graph.number_of_nodes() == 0:
            return metrics

        # 1. Degrees
        in_degrees = dict(self.graph.in_degree())
        out_degrees = dict(self.graph.out_degree())
        total_degrees = dict(self.graph.degree())

        # 2. PageRank
        try:
            pagerank = nx.pagerank(self.simple_digraph, alpha=0.85, max_iter=100)
        except Exception:
            pagerank = {n: 1.0 / max(1, len(self.simple_digraph)) for n in self.simple_digraph.nodes()}

        # 3. Betweenness Centrality (sample-k for large graphs to prevent GUI delays)
        num_nodes = len(self.simple_digraph)
        k_samples = min(num_nodes, 100) if num_nodes > 200 else None
        try:
            betweenness = nx.betweenness_centrality(self.simple_digraph, k=k_samples, normalized=True)
        except Exception:
            betweenness = {n: 0.0 for n in self.simple_digraph.nodes()}

        # 4. Clustering Coefficient
        try:
            clustering = nx.clustering(self.simple_undirected)
        except Exception:
            clustering = {n: 0.0 for n in self.simple_undirected.nodes()}

        # 5. Connected Components sizes
        components = list(nx.connected_components(self.simple_undirected))
        component_sizes: Dict[str, int] = {}
        for comp in components:
            sz = len(comp)
            for node in comp:
                component_sizes[node] = sz

        for node in self.graph.nodes():
            in_d = in_degrees.get(node, 0)
            out_d = out_degrees.get(node, 0)
            tot_d = total_degrees.get(node, 0)
            
            fan_in = in_d / max(1, tot_d)
            fan_out = out_d / max(1, tot_d)

            metrics[node] = {
                "degree": float(tot_d),
                "in_degree": float(in_d),
                "out_degree": float(out_d),
                "fan_in_ratio": round(fan_in, 4),
                "fan_out_ratio": round(fan_out, 4),
                "pagerank": round(pagerank.get(node, 0.0), 6),
                "betweenness": round(betweenness.get(node, 0.0), 6),
                "clustering_coefficient": round(clustering.get(node, 0.0), 6),
                "component_size": float(component_sizes.get(node, 1)),
            }

        return metrics
