"""NetworkX heterogeneous graph builder for Bitcoin transaction metadata."""
import logging
import networkx as nx
from typing import List, Dict, Any, Optional, Set
from core.enums import NodeType, EdgeType
from core.models import TransactionRecord, Entity

logger = logging.getLogger("TRACE.GraphBuilder")


class GraphBuilder:
    """Constructs forensic multigraph linking IPs, transactions, wallets, and resolved entities."""

    def __init__(self):
        self.graph = nx.MultiDiGraph()

    def build_graph(
        self,
        records: List[TransactionRecord],
        entities: Optional[Dict[str, Entity]] = None,
        cio_links: Optional[List[Dict[str, Any]]] = None,
    ) -> nx.MultiDiGraph:
        """Construct the heterogeneous multi-directed graph."""
        self.graph.clear()

        # Track node attributes
        ip_metadata: Dict[str, Dict[str, Any]] = {}
        wallet_metadata: Dict[str, Dict[str, Any]] = {}

        # 1. Add Transaction and Network nodes & edges
        for r in records:
            tx_node = f"TX_{r.txid[:16]}"
            tx_amount = r.total_output_amount

            # Add Transaction Node
            self.graph.add_node(
                tx_node,
                node_type=NodeType.TRANSACTION.value,
                txid=r.txid,
                timestamp=r.timestamp,
                amount=tx_amount,
                fee=r.fee,
                input_count=r.input_count,
                output_count=r.output_count,
                label=f"TX: {r.txid[:8]}...",
            )

            # Add IP Node & OBSERVED edge
            if r.src_ip:
                ip_node = f"IP_{r.src_ip}"
                if ip_node not in ip_metadata:
                    ip_metadata[ip_node] = {
                        "ip": r.src_ip,
                        "country": r.geo_country,
                        "asn": r.asn,
                        "tx_count": 0,
                        "wallets": set(),
                    }
                ip_metadata[ip_node]["tx_count"] += 1
                for addr in r.input_addresses + r.output_addresses:
                    ip_metadata[ip_node]["wallets"].add(addr)

                self.graph.add_node(
                    ip_node,
                    node_type=NodeType.IP.value,
                    ip=r.src_ip,
                    country=r.geo_country,
                    asn=r.asn,
                    label=f"IP: {r.src_ip}",
                )

                self.graph.add_edge(
                    ip_node,
                    tx_node,
                    edge_type=EdgeType.OBSERVED.value,
                    confidence=1.0,
                    label="OBSERVED",
                )

            # Add Wallet Inputs & INPUT edges (Wallet -> TX)
            for idx, in_addr in enumerate(r.input_addresses):
                if not in_addr:
                    continue
                w_node = f"WAL_{in_addr[:14]}"
                amt = r.input_amounts[idx] if idx < len(r.input_amounts) else 0.0

                if w_node not in wallet_metadata:
                    wallet_metadata[w_node] = {"address": in_addr, "total_in": 0.0, "total_out": 0.0, "tx_count": 0}
                wallet_metadata[w_node]["total_out"] += amt
                wallet_metadata[w_node]["tx_count"] += 1

                self.graph.add_node(
                    w_node,
                    node_type=NodeType.WALLET.value,
                    address=in_addr,
                    label=f"WAL: {in_addr[:8]}...",
                )

                self.graph.add_edge(
                    w_node,
                    tx_node,
                    edge_type=EdgeType.INPUT.value,
                    amount=amt,
                    label=f"INPUT ({amt:.4f})",
                )

            # Add Wallet Outputs & OUTPUT edges (TX -> Wallet)
            for idx, out_addr in enumerate(r.output_addresses):
                if not out_addr:
                    continue
                w_node = f"WAL_{out_addr[:14]}"
                amt = r.output_amounts[idx] if idx < len(r.output_amounts) else 0.0

                if w_node not in wallet_metadata:
                    wallet_metadata[w_node] = {"address": out_addr, "total_in": 0.0, "total_out": 0.0, "tx_count": 0}
                wallet_metadata[w_node]["total_in"] += amt
                wallet_metadata[w_node]["tx_count"] += 1

                self.graph.add_node(
                    w_node,
                    node_type=NodeType.WALLET.value,
                    address=out_addr,
                    label=f"WAL: {out_addr[:8]}...",
                )

                self.graph.add_edge(
                    tx_node,
                    w_node,
                    edge_type=EdgeType.OUTPUT.value,
                    amount=amt,
                    label=f"OUTPUT ({amt:.4f})",
                )

        # Update node metadata
        for ip_node, meta in ip_metadata.items():
            if self.graph.has_node(ip_node):
                self.graph.nodes[ip_node]["tx_count"] = meta["tx_count"]
                self.graph.nodes[ip_node]["wallet_count"] = len(meta["wallets"])

        for w_node, meta in wallet_metadata.items():
            if self.graph.has_node(w_node):
                self.graph.nodes[w_node]["total_in"] = meta["total_in"]
                self.graph.nodes[w_node]["total_out"] = meta["total_out"]
                self.graph.nodes[w_node]["tx_count"] = meta["tx_count"]

        # 2. Add Common Input Ownership edges
        if cio_links:
            for link in cio_links:
                w1 = f"WAL_{link['source_address'][:14]}"
                w2 = f"WAL_{link['target_address'][:14]}"
                if self.graph.has_node(w1) and self.graph.has_node(w2):
                    self.graph.add_edge(
                        w1,
                        w2,
                        edge_type=EdgeType.COMMON_INPUT.value,
                        confidence=link["confidence"],
                        co_spending_count=link["co_spending_count"],
                        label="COMMON_INPUT",
                    )

        # 3. Add Resolved Entity & Cluster nodes if available
        if entities:
            for ent_id, ent in entities.items():
                if len(ent.addresses) > 1:
                    e_node = f"ENT_{ent_id}"
                    self.graph.add_node(
                        e_node,
                        node_type=NodeType.ENTITY.value,
                        entity_id=ent_id,
                        address_count=len(ent.addresses),
                        label=f"Entity: {ent_id[:10]}",
                    )
                    for a in ent.addresses:
                        w_node = f"WAL_{a[:14]}"
                        if self.graph.has_node(w_node):
                            self.graph.add_edge(
                                w_node,
                                e_node,
                                edge_type=EdgeType.MEMBER_OF.value,
                                label="MEMBER_OF",
                            )

        logger.info(f"Graph built: {self.graph.number_of_nodes()} nodes, {self.graph.number_of_edges()} edges")
        return self.graph
