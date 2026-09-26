"""Entity resolution engine implementing the Common Input Ownership (CIO) heuristic."""
import logging
import hashlib
from typing import Dict, List, Set, Any, Tuple
from core.enums import NodeType, EdgeType
from core.models import TransactionRecord, Entity
from core.constants import STATUS_DESCRIPTIONS

logger = logging.getLogger("TRACE.EntityResolution")


class DisjointSetUnion:
    """Disjoint Set Union (Union-Find) with path compression and union by rank."""

    def __init__(self):
        self.parent: Dict[str, str] = {}
        self.rank: Dict[str, int] = {}

    def find(self, item: str) -> str:
        if item not in self.parent:
            self.parent[item] = item
            self.rank[item] = 0
            return item
        if self.parent[item] != item:
            self.parent[item] = self.find(self.parent[item])
        return self.parent[item]

    def union(self, item1: str, item2: str):
        root1 = self.find(item1)
        root2 = self.find(item2)
        if root1 != root2:
            if self.rank[root1] < self.rank[root2]:
                self.parent[root1] = root2
            elif self.rank[root1] > self.rank[root2]:
                self.parent[root2] = root1
            else:
                self.parent[root2] = root1
                self.rank[root1] += 1


class EntityResolver:
    """Resolves wallet addresses into provisional behavioral entities via Common-Input Heuristic."""

    def __init__(self, min_supporting_tx: int = 1):
        self.dsu = DisjointSetUnion()
        self.co_spending_counts: Dict[Tuple[str, str], int] = {}
        self.co_spending_txids: Dict[Tuple[str, str], List[str]] = {}
        self.min_supporting_tx = min_supporting_tx
        self.resolved_entities: Dict[str, Entity] = {}
        self.address_to_entity_id: Dict[str, str] = {}

    def resolve_entities(self, records: List[TransactionRecord]) -> Dict[str, Entity]:
        """
        Group co-spent input addresses into heuristic clusters.
        Single addresses not co-spent become single-address entities.
        """
        self.dsu = DisjointSetUnion()
        self.co_spending_counts.clear()
        self.co_spending_txids.clear()
        self.resolved_entities.clear()
        self.address_to_entity_id.clear()

        # 1. Apply CIO heuristic on inputs of each transaction
        all_addresses: Set[str] = set()
        for r in records:
            inputs = [addr for addr in r.input_addresses if addr]
            outputs = [addr for addr in r.output_addresses if addr]
            for a in inputs + outputs:
                all_addresses.add(a)

            if len(inputs) > 1:
                base_addr = inputs[0]
                for other_addr in inputs[1:]:
                    self.dsu.union(base_addr, other_addr)
                    pair = tuple(sorted([base_addr, other_addr]))
                    self.co_spending_counts[pair] = self.co_spending_counts.get(pair, 0) + 1
                    self.co_spending_txids.setdefault(pair, []).append(r.txid)

        # 2. Group addresses by DSU root
        cluster_groups: Dict[str, List[str]] = {}
        for addr in all_addresses:
            root = self.dsu.find(addr)
            cluster_groups.setdefault(root, []).append(addr)

        # 3. Create Entity objects
        for root, member_addrs in cluster_groups.items():
            if len(member_addrs) > 1:
                # Multi-address cluster
                h = hashlib.sha256("_".join(sorted(member_addrs)).encode()).hexdigest()[:10]
                entity_id = f"ENT_CIO_{h}"
                ent_type = NodeType.ENTITY
            else:
                entity_id = f"ENT_WAL_{member_addrs[0][:10]}"
                ent_type = NodeType.WALLET

            for addr in member_addrs:
                self.address_to_entity_id[addr] = entity_id

            # Find all txids and IPs involved with these member addresses
            ent_txids = set()
            ent_ips = set()
            tot_in = 0.0
            tot_out = 0.0

            for r in records:
                is_input = any(a in member_addrs for a in r.input_addresses)
                is_output = any(a in member_addrs for a in r.output_addresses)
                if is_input or is_output:
                    ent_txids.add(r.txid)
                    if r.src_ip:
                        ent_ips.add(r.src_ip)
                    if is_input:
                        tot_out += r.total_input_amount
                    if is_output:
                        tot_in += r.total_output_amount

            entity = Entity(
                entity_id=entity_id,
                entity_type=ent_type,
                addresses=member_addrs,
                ips=list(ent_ips),
                txids=list(ent_txids),
                transaction_count=len(ent_txids),
                total_in=tot_in,
                total_out=tot_out,
                unique_ips=len(ent_ips),
            )
            self.resolved_entities[entity_id] = entity

        return self.resolved_entities

    def get_entity_id_for_address(self, address: str) -> str:
        return self.address_to_entity_id.get(address, f"ENT_WAL_{address[:10]}")

    def get_cio_relationships(self) -> List[Dict[str, Any]]:
        """Return explainable list of CIO heuristic links."""
        links = []
        for (addr1, addr2), count in self.co_spending_counts.items():
            txids = self.co_spending_txids.get((addr1, addr2), [])
            confidence = min(0.95, 0.75 + (count * 0.05))
            links.append({
                "source_address": addr1,
                "target_address": addr2,
                "relationship_type": EdgeType.COMMON_INPUT.value,
                "co_spending_count": count,
                "supporting_transactions": txids,
                "confidence": confidence,
                "forensic_label": STATUS_DESCRIPTIONS["CIO_HEURISTIC"],
            })
        return links
