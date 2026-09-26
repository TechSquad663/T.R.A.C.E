"""Graph embeddings using Spectral Matrix Factorization (Node2Vec approximation)."""
import logging
import networkx as nx
import numpy as np
from sklearn.decomposition import TruncatedSVD
from typing import Dict

logger = logging.getLogger("TRACE.Embeddings")

class GraphEmbedder:
    """Generates structural node embeddings using Spectral decomposition."""
    
    def __init__(self, dimensions: int = 8):
        self.dimensions = dimensions
        
    def fit_transform(self, G: nx.DiGraph) -> Dict[str, np.ndarray]:
        """
        Approximate Node2Vec using Truncated SVD on the graph adjacency matrix.
        Returns a dictionary mapping node_id to embedding vector.
        """
        if G.number_of_nodes() < self.dimensions + 1:
            logger.warning("Graph too small for requested embedding dimensions.")
            dim = max(1, G.number_of_nodes() - 1)
        else:
            dim = self.dimensions
            
        logger.info(f"Generating {dim}-dimensional graph embeddings...")
        
        nodes = list(G.nodes())
        if not nodes:
            return {}
            
        # Get sparse adjacency matrix
        adj = nx.to_scipy_sparse_array(G, nodelist=nodes, weight='weight', dtype=float)
        
        # Factorize using SVD (spectral approximation of DeepWalk/Node2Vec)
        svd = TruncatedSVD(n_components=dim, random_state=42)
        try:
            embeddings_matrix = svd.fit_transform(adj)
        except Exception as e:
            logger.error(f"SVD embedding failed: {e}")
            embeddings_matrix = np.zeros((len(nodes), dim))
            
        # Map back to node IDs
        embeddings = {
            str(nodes[i]): embeddings_matrix[i]
            for i in range(len(nodes))
        }
        
        return embeddings
