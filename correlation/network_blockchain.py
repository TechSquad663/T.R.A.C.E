"""Network <-> Blockchain layer correlation engine."""
import logging
from typing import List, Dict, Any, Set
from core.models import TransactionRecord, NetworkObservation
from core.constants import STATUS_DESCRIPTIONS

logger = logging.getLogger("TRACE.NetChainCorrelator")


class NetworkBlockchainCorrelator:
    """Correlates network packet/session metadata with on-chain ledger activity."""

    def __init__(self):
        self.ip_to_txids: Dict[str, Set[str]] = {}
        self.ip_to_wallets: Dict[str, Set[str]] = {}
        self.wallet_to_ips: Dict[str, Set[str]] = {}
        self.wallet_to_txids: Dict[str, Set[str]] = {}
        self.txid_to_ips: Dict[str, Set[str]] = {}
        self.correlations: List[Dict[str, Any]] = []

    def correlate(self, records: List[TransactionRecord]) -> Dict[str, Any]:
        """Process transaction records and build bidirectional association index."""
        self.ip_to_txids.clear()
        self.ip_to_wallets.clear()
        self.wallet_to_ips.clear()
        self.wallet_to_txids.clear()
        self.txid_to_ips.clear()
        self.correlations.clear()

        for r in records:
            txid = r.txid
            src_ip = r.src_ip
            wallets = set(r.input_addresses + r.output_addresses)

            # Record IP -> TXID
            if src_ip:
                self.ip_to_txids.setdefault(src_ip, set()).add(txid)
                self.txid_to_ips.setdefault(txid, set()).add(src_ip)

                # Contextual link IP <-> Wallets
                for w in wallets:
                    self.ip_to_wallets.setdefault(src_ip, set()).add(w)
                    self.wallet_to_ips.setdefault(w, set()).add(src_ip)

            # Record Wallet <-> TXID
            for w in wallets:
                self.wallet_to_txids.setdefault(w, set()).add(txid)

            # Generate formal correlation record with evidentiary disclaimer
            corr_entry = {
                "txid": txid,
                "src_ip": src_ip,
                "dst_ip": r.dst_ip,
                "timestamp": r.timestamp,
                "input_wallets": r.input_addresses,
                "output_wallets": r.output_addresses,
                "geo_country": r.geo_country,
                "asn": r.asn,
                "relationship_type": "OBSERVED_RELAY",
                "confidence": 0.90 if src_ip else 0.0,
                "legal_disclaimer": STATUS_DESCRIPTIONS["IP_CORRELATION"],
            }
            self.correlations.append(corr_entry)

        return {
            "total_correlated_transactions": len(records),
            "unique_ips": len(self.ip_to_txids),
            "unique_wallets": len(self.wallet_to_txids),
            "associations_count": len(self.correlations),
        }

    def get_ips_for_wallet(self, wallet_address: str) -> List[str]:
        return list(self.wallet_to_ips.get(wallet_address, set()))

    def get_wallets_for_ip(self, ip_address: str) -> List[str]:
        return list(self.ip_to_wallets.get(ip_address, set()))

    def get_txids_for_wallet(self, wallet_address: str) -> List[str]:
        return list(self.wallet_to_txids.get(wallet_address, set()))

    def get_txids_for_ip(self, ip_address: str) -> List[str]:
        return list(self.ip_to_txids.get(ip_address, set()))
