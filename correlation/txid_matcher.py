"""TXID-based cryptographic matcher correlating network layer and blockchain layer."""
import logging
from typing import Dict, List, Any, Optional
from core.models import TransactionRecord, NetworkObservation

logger = logging.getLogger("TRACE.TXIDMatcher")


class TXIDMatcher:
    """Performs direct hash correlation between P2P network traffic and blockchain ledger records."""

    def __init__(self):
        self.txid_to_record: Dict[str, TransactionRecord] = {}
        self.txid_to_observations: Dict[str, List[NetworkObservation]] = {}

    def index_records(self, records: List[TransactionRecord]):
        """Index transactions by TXID."""
        self.txid_to_record.clear()
        self.txid_to_observations.clear()

        for r in records:
            if not r.txid:
                continue
            self.txid_to_record[r.txid] = r
            
            # Create network observation entry
            obs = NetworkObservation(
                observation_id=f"obs_{r.txid[:12]}_{r.src_ip}",
                src_ip=r.src_ip,
                dst_ip=r.dst_ip,
                src_port=r.src_port,
                dst_port=r.dst_port,
                timestamp=r.timestamp,
                txid=r.txid,
                geo_country=r.geo_country,
                asn=r.asn,
                correlation_confidence=1.0,  # Direct cryptographic match
            )
            self.txid_to_observations.setdefault(r.txid, []).append(obs)

    def get_by_txid(self, txid: str) -> Optional[TransactionRecord]:
        return self.txid_to_record.get(txid)

    def get_network_observations(self, txid: str) -> List[NetworkObservation]:
        return self.txid_to_observations.get(txid, [])
