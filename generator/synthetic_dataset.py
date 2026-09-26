"""Synthetic Bitcoin P2P and blockchain transaction metadata generator.

Produces realistic behavioral scenarios for offline forensic analysis while
strictly maintaining ground truth isolation from ML model input features.
"""

import hashlib
import random
import json
import csv
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional, Union
from core.enums import BehaviorPattern


# Reference Geo/ASN pools for realistic network metadata
GEO_POOLS = [
    ("US", "AS15169 Google LLC"),
    ("DE", "AS24940 Hetzner Online GmbH"),
    ("NL", "AS60781 LeaseWeb Netherlands"),
    ("CH", "AS13030 SWITCH Switzerland"),
    ("SG", "AS45102 Alibaba Cloud"),
    ("JP", "AS2516 KDDI Corporation"),
    ("GB", "AS2856 British Telecommunications"),
    ("CA", "AS577 Bell Canada"),
    ("FR", "AS16276 OVH SAS"),
    ("SE", "AS3301 Telia Company AB"),
    ("RU", "AS12389 Rostelecom"),
    ("IS", "AS44547 Verne Global"),
    ("PA", "AS27775 Cable & Wireless Panama"),
    ("SC", "AS327777 Seychelles Telecom"),
]

SCRIPT_TYPES = ["P2PKH", "P2SH", "P2WPKH", "P2WSH", "P2TR"]


def generate_btc_address(rng: random.Random, prefix_type: str = "bc1q") -> str:
    """Generate realistic-looking Bitcoin address."""
    charset = "023456789acdefghjklmnpqrstuvwxyz"
    if prefix_type == "1":
        # Legacy P2PKH (base58)
        b58 = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
        suffix = "".join(rng.choice(b58) for _ in range(33))
        return "1" + suffix
    elif prefix_type == "3":
        # P2SH (base58)
        b58 = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
        suffix = "".join(rng.choice(b58) for _ in range(33))
        return "3" + suffix
    else:
        # SegWit Bech32
        suffix = "".join(rng.choice(charset) for _ in range(38))
        return "bc1q" + suffix


def generate_txid(rng: random.Random, salt: str) -> str:
    """Generate deterministic 64-hex char TXID."""
    h = hashlib.sha256(f"{salt}_{rng.randint(0, 10**12)}".encode()).hexdigest()
    return h


def generate_random_ip(rng: random.Random, subnet_prefix: Optional[str] = None) -> str:
    """Generate realistic public IPv4 address."""
    if subnet_prefix:
        return f"{subnet_prefix}.{rng.randint(2, 254)}"
    # Avoid 0.x, 10.x, 127.x, 192.168.x, 224+.x
    o1 = rng.choice([45, 62, 78, 89, 93, 104, 134, 151, 168, 178, 185, 198, 203, 212])
    return f"{o1}.{rng.randint(10, 240)}.{rng.randint(1, 254)}.{rng.randint(2, 254)}"


class SyntheticBitcoinTrafficGenerator:
    """Generates synthetic Bitcoin P2P network and blockchain transaction metadata."""

    def __init__(self, seed: int = 42):
        self.seed = seed
        self.rng = random.Random(seed)

    def generate_dataset(
        self,
        num_transactions: int = 1200,
        start_time: Optional[datetime] = None,
        anomaly_ratio: float = 0.22,
    ) -> Tuple[List[Dict[str, Any]], Dict[str, Dict[str, Any]]]:
        """
        Generate synthetic transactions and isolated ground truth labels.
        Returns:
            (records: List[Dict[str, Any]], ground_truth: Dict[str, Dict[str, Any]])
        """
        self.rng.seed(self.seed)
        if start_time is None:
            start_time = datetime(2026, 3, 1, 10, 0, 0, tzinfo=timezone.utc)

        records: List[Dict[str, Any]] = []
        ground_truth: Dict[str, Dict[str, Any]] = {}  # Keyed by entity address or txid

        current_time = start_time
        tx_counter = 0

        # Scenario distribution calculation
        num_anomalies = int(num_transactions * anomaly_ratio)
        num_normal = num_transactions - num_anomalies

        # 1. Normal traffic baseline
        normal_wallets = [generate_btc_address(self.rng) for _ in range(120)]
        normal_ips = [generate_random_ip(self.rng) for _ in range(40)]

        for i in range(num_normal):
            tx_counter += 1
            current_time += timedelta(seconds=self.rng.randint(15, 180))
            txid = generate_txid(self.rng, f"norm_{tx_counter}")

            in_wallet = self.rng.choice(normal_wallets)
            out_wallet1 = self.rng.choice(normal_wallets)
            out_wallet2 = generate_btc_address(self.rng)  # change address
            ip = self.rng.choice(normal_ips)
            geo, asn = self.rng.choice(GEO_POOLS[:6])

            amt = round(self.rng.uniform(0.005, 1.8), 8)
            fee = round(self.rng.uniform(0.00005, 0.0003), 8)
            out1 = round(amt * self.rng.uniform(0.3, 0.7), 8)
            out2 = round(amt - out1 - fee, 8)

            record = {
                "timestamp": current_time.isoformat(),
                "src_ip": ip,
                "dst_ip": generate_random_ip(self.rng),
                "src_port": self.rng.randint(10240, 65000),
                "dst_port": 8333,
                "txid": txid,
                "input_addresses": [in_wallet],
                "output_addresses": [out_wallet1, out_wallet2],
                "input_amounts": [amt],
                "output_amounts": [out1, max(0.00001, out2)],
                "fee": fee,
                "script_type": self.rng.choice(SCRIPT_TYPES),
                "geo_country": geo,
                "asn": asn,
            }
            records.append(record)
            ground_truth[txid] = {
                "scenario": BehaviorPattern.NORMAL.value,
                "is_suspicious": 0,
                "notes": "Standard standard P2P transaction",
            }
            ground_truth[in_wallet] = {
                "scenario": BehaviorPattern.NORMAL.value,
                "is_suspicious": 0,
            }

        # 2. Behavioral Anomaly Scenarios
        scenario_types = [
            (BehaviorPattern.BURST, 0.15),
            (BehaviorPattern.FAN_IN, 0.15),
            (BehaviorPattern.FAN_OUT, 0.15),
            (BehaviorPattern.CHAIN, 0.15),
            (BehaviorPattern.MULTI_IP, 0.10),
            (BehaviorPattern.MULTI_COUNTRY, 0.10),
            (BehaviorPattern.DORMANT_ACTIVATION, 0.10),
            (BehaviorPattern.HIGH_VELOCITY, 0.10),
        ]

        for pattern, weight in scenario_types:
            scenario_count = max(5, int(num_anomalies * weight))
            if pattern == BehaviorPattern.BURST:
                # Same entity sending 10-20 transactions within a 30-second window
                burst_wallet = generate_btc_address(self.rng, "bc1q")
                burst_ip = generate_random_ip(self.rng)
                geo, asn = GEO_POOLS[1]
                burst_start = current_time + timedelta(minutes=self.rng.randint(10, 60))

                for b in range(scenario_count):
                    tx_counter += 1
                    b_time = burst_start + timedelta(seconds=b * 2)
                    txid = generate_txid(self.rng, f"burst_{tx_counter}")
                    recip = generate_btc_address(self.rng)
                    amt = round(self.rng.uniform(0.1, 0.5), 8)
                    fee = 0.0002

                    records.append({
                        "timestamp": b_time.isoformat(),
                        "src_ip": burst_ip,
                        "dst_ip": generate_random_ip(self.rng),
                        "src_port": self.rng.randint(20000, 60000),
                        "dst_port": 8333,
                        "txid": txid,
                        "input_addresses": [burst_wallet],
                        "output_addresses": [recip],
                        "input_amounts": [round(amt + fee, 8)],
                        "output_amounts": [amt],
                        "fee": fee,
                        "script_type": "P2WPKH",
                        "geo_country": geo,
                        "asn": asn,
                    })
                    ground_truth[txid] = {
                        "scenario": pattern.value,
                        "is_suspicious": 1,
                        "notes": "Automated rapid burst activity",
                    }
                ground_truth[burst_wallet] = {
                    "scenario": pattern.value,
                    "is_suspicious": 1,
                    "notes": "Source of rapid automated transaction burst",
                }

            elif pattern == BehaviorPattern.FAN_OUT:
                # 1 input dispersing into 15-25 addresses
                fan_wallet = generate_btc_address(self.rng, "3")
                fan_ip = generate_random_ip(self.rng)
                geo, asn = GEO_POOLS[2]
                fan_start = current_time + timedelta(minutes=self.rng.randint(15, 90))

                for f_idx in range(max(2, scenario_count // 5)):
                    tx_counter += 1
                    txid = generate_txid(self.rng, f"fanout_{tx_counter}")
                    recips = [generate_btc_address(self.rng) for _ in range(16)]
                    total_amt = round(self.rng.uniform(10.0, 45.0), 8)
                    each_amt = round((total_amt - 0.001) / len(recips), 8)

                    records.append({
                        "timestamp": (fan_start + timedelta(minutes=f_idx * 5)).isoformat(),
                        "src_ip": fan_ip,
                        "dst_ip": generate_random_ip(self.rng),
                        "src_port": 8333,
                        "dst_port": 8333,
                        "txid": txid,
                        "input_addresses": [fan_wallet],
                        "output_addresses": recips,
                        "input_amounts": [total_amt],
                        "output_amounts": [each_amt] * len(recips),
                        "fee": 0.001,
                        "script_type": "P2SH",
                        "geo_country": geo,
                        "asn": asn,
                    })
                    ground_truth[txid] = {
                        "scenario": pattern.value,
                        "is_suspicious": 1,
                        "notes": "High fan-out fund dispersion",
                    }
                ground_truth[fan_wallet] = {
                    "scenario": pattern.value,
                    "is_suspicious": 1,
                    "notes": "Entity exhibiting extreme fan-out dispersion",
                }

            elif pattern == BehaviorPattern.FAN_IN:
                # Many inputs funneling into 1 recipient
                collector_wallet = generate_btc_address(self.rng, "1")
                collector_ip = generate_random_ip(self.rng)
                geo, asn = GEO_POOLS[3]
                fin_start = current_time + timedelta(minutes=self.rng.randint(20, 120))

                for fin_idx in range(max(2, scenario_count // 5)):
                    tx_counter += 1
                    txid = generate_txid(self.rng, f"fanin_{tx_counter}")
                    feeders = [generate_btc_address(self.rng) for _ in range(12)]
                    feeder_amts = [round(self.rng.uniform(0.5, 2.0), 8) for _ in range(12)]
                    tot_in = sum(feeder_amts)
                    fee = 0.0008

                    records.append({
                        "timestamp": (fin_start + timedelta(minutes=fin_idx * 8)).isoformat(),
                        "src_ip": collector_ip,
                        "dst_ip": generate_random_ip(self.rng),
                        "src_port": 8333,
                        "dst_port": 8333,
                        "txid": txid,
                        "input_addresses": feeders,
                        "output_addresses": [collector_wallet],
                        "input_amounts": feeder_amts,
                        "output_amounts": [round(tot_in - fee, 8)],
                        "fee": fee,
                        "script_type": "P2PKH",
                        "geo_country": geo,
                        "asn": asn,
                    })
                    ground_truth[txid] = {
                        "scenario": pattern.value,
                        "is_suspicious": 1,
                        "notes": "Multi-input consolidation / fan-in",
                    }
                    for fdr in feeders:
                        ground_truth[fdr] = {"scenario": pattern.value, "is_suspicious": 1}
                ground_truth[collector_wallet] = {
                    "scenario": pattern.value,
                    "is_suspicious": 1,
                    "notes": "Aggregation endpoint for multi-input consolidation",
                }

            elif pattern == BehaviorPattern.CHAIN:
                # Rapid passthrough chain: W1 -> W2 -> W3 -> W4
                hops = min(scenario_count, 8)
                chain_wallets = [generate_btc_address(self.rng) for _ in range(hops + 1)]
                chain_ip = generate_random_ip(self.rng)
                geo, asn = GEO_POOLS[4]
                chain_time = current_time + timedelta(hours=2)
                curr_amt = round(self.rng.uniform(5.0, 15.0), 8)

                for hop in range(hops):
                    tx_counter += 1
                    txid = generate_txid(self.rng, f"chain_{tx_counter}")
                    chain_time += timedelta(seconds=self.rng.randint(5, 30))  # rapid hop
                    fee = 0.0003
                    out_amt = round(curr_amt - fee, 8)

                    records.append({
                        "timestamp": chain_time.isoformat(),
                        "src_ip": chain_ip,
                        "dst_ip": generate_random_ip(self.rng),
                        "src_port": 8333,
                        "dst_port": 8333,
                        "txid": txid,
                        "input_addresses": [chain_wallets[hop]],
                        "output_addresses": [chain_wallets[hop + 1]],
                        "input_amounts": [curr_amt],
                        "output_amounts": [out_amt],
                        "fee": fee,
                        "script_type": "P2WPKH",
                        "geo_country": geo,
                        "asn": asn,
                    })
                    curr_amt = out_amt
                    ground_truth[txid] = {
                        "scenario": pattern.value,
                        "is_suspicious": 1,
                        "notes": f"Rapid sequential transfer hop #{hop+1}",
                    }
                    ground_truth[chain_wallets[hop]] = {
                        "scenario": pattern.value,
                        "is_suspicious": 1,
                        "notes": "Intermediate transit node in rapid chain",
                    }

            elif pattern == BehaviorPattern.MULTI_IP:
                # Single wallet relayed via 6 different IP addresses within 10 minutes
                multi_wallet = generate_btc_address(self.rng, "bc1q")
                multi_ips = [generate_random_ip(self.rng) for _ in range(6)]
                m_time = current_time + timedelta(hours=3)

                for m_idx in range(min(scenario_count, len(multi_ips))):
                    tx_counter += 1
                    txid = generate_txid(self.rng, f"multi_ip_{tx_counter}")
                    m_time += timedelta(seconds=45)
                    ip = multi_ips[m_idx]
                    geo, asn = self.rng.choice(GEO_POOLS)
                    amt = round(self.rng.uniform(1.0, 3.5), 8)

                    records.append({
                        "timestamp": m_time.isoformat(),
                        "src_ip": ip,
                        "dst_ip": generate_random_ip(self.rng),
                        "src_port": self.rng.randint(30000, 65000),
                        "dst_port": 8333,
                        "txid": txid,
                        "input_addresses": [multi_wallet],
                        "output_addresses": [generate_btc_address(self.rng)],
                        "input_amounts": [amt],
                        "output_amounts": [round(amt - 0.0002, 8)],
                        "fee": 0.0002,
                        "script_type": "P2TR",
                        "geo_country": geo,
                        "asn": asn,
                    })
                    ground_truth[txid] = {
                        "scenario": pattern.value,
                        "is_suspicious": 1,
                        "notes": "Transaction relayed via proxy/VPN node",
                    }
                ground_truth[multi_wallet] = {
                    "scenario": pattern.value,
                    "is_suspicious": 1,
                    "notes": "Entity associated with multiple disparate IP addresses and ASNs",
                }

            elif pattern == BehaviorPattern.MULTI_COUNTRY:
                # Same wallet observed broadcasting from Panama, Russia, Netherlands, Seychelles in 15 mins
                intl_wallet = generate_btc_address(self.rng, "3")
                countries = [GEO_POOLS[2], GEO_POOLS[10], GEO_POOLS[12], GEO_POOLS[13]]
                c_time = current_time + timedelta(hours=4)

                for c_idx in range(min(scenario_count, len(countries))):
                    tx_counter += 1
                    txid = generate_txid(self.rng, f"multicountry_{tx_counter}")
                    c_time += timedelta(minutes=2)
                    geo, asn = countries[c_idx]
                    amt = round(self.rng.uniform(2.0, 6.0), 8)

                    records.append({
                        "timestamp": c_time.isoformat(),
                        "src_ip": generate_random_ip(self.rng),
                        "dst_ip": generate_random_ip(self.rng),
                        "src_port": 8333,
                        "dst_port": 8333,
                        "txid": txid,
                        "input_addresses": [intl_wallet],
                        "output_addresses": [generate_btc_address(self.rng)],
                        "input_amounts": [amt],
                        "output_amounts": [round(amt - 0.0003, 8)],
                        "fee": 0.0003,
                        "script_type": "P2SH",
                        "geo_country": geo,
                        "asn": asn,
                    })
                    ground_truth[txid] = {
                        "scenario": pattern.value,
                        "is_suspicious": 1,
                        "notes": "Geographically anomalous cross-border transmission",
                    }
                ground_truth[intl_wallet] = {
                    "scenario": pattern.value,
                    "is_suspicious": 1,
                    "notes": "Entity exhibiting anomalous cross-jurisdictional relaying",
                }

            elif pattern == BehaviorPattern.DORMANT_ACTIVATION:
                # Wallet dormant for 2 years suddenly moves 50 BTC
                dormant_wallet = generate_btc_address(self.rng, "1")
                d_time = current_time + timedelta(days=700)
                tx_counter += 1
                txid = generate_txid(self.rng, f"dormant_{tx_counter}")
                amt = round(self.rng.uniform(25.0, 80.0), 8)

                records.append({
                    "timestamp": d_time.isoformat(),
                    "src_ip": generate_random_ip(self.rng),
                    "dst_ip": generate_random_ip(self.rng),
                    "src_port": 8333,
                    "dst_port": 8333,
                    "txid": txid,
                    "input_addresses": [dormant_wallet],
                    "output_addresses": [generate_btc_address(self.rng), generate_btc_address(self.rng)],
                    "input_amounts": [amt],
                    "output_amounts": [round(amt * 0.4, 8), round(amt * 0.6 - 0.001, 8)],
                    "fee": 0.001,
                    "script_type": "P2PKH",
                    "geo_country": GEO_POOLS[0][0],
                    "asn": GEO_POOLS[0][1],
                })
                ground_truth[txid] = {
                    "scenario": pattern.value,
                    "is_suspicious": 1,
                    "notes": "Sudden activation after prolonged dormancy",
                }
                ground_truth[dormant_wallet] = {
                    "scenario": pattern.value,
                    "is_suspicious": 1,
                    "notes": "Prolonged dormant wallet activation",
                }

            elif pattern == BehaviorPattern.HIGH_VELOCITY:
                velo_wallet = generate_btc_address(self.rng, "bc1q")
                velo_ip = generate_random_ip(self.rng)
                v_time = current_time + timedelta(hours=5)

                for v in range(scenario_count):
                    tx_counter += 1
                    txid = generate_txid(self.rng, f"velo_{tx_counter}")
                    v_time += timedelta(seconds=self.rng.randint(3, 8))
                    amt = round(self.rng.uniform(0.5, 3.0), 8)

                    records.append({
                        "timestamp": v_time.isoformat(),
                        "src_ip": velo_ip,
                        "dst_ip": generate_random_ip(self.rng),
                        "src_port": 8333,
                        "dst_port": 8333,
                        "txid": txid,
                        "input_addresses": [velo_wallet],
                        "output_addresses": [generate_btc_address(self.rng)],
                        "input_amounts": [amt],
                        "output_amounts": [round(amt - 0.0002, 8)],
                        "fee": 0.0002,
                        "script_type": "P2WPKH",
                        "geo_country": GEO_POOLS[1][0],
                        "asn": GEO_POOLS[1][1],
                    })
                    ground_truth[txid] = {
                        "scenario": pattern.value,
                        "is_suspicious": 1,
                        "notes": "High transaction velocity flow",
                    }
                ground_truth[velo_wallet] = {
                    "scenario": pattern.value,
                    "is_suspicious": 1,
                    "notes": "High velocity relaying entity",
                }

        # Sort all records chronologically
        records.sort(key=lambda r: r["timestamp"])
        return records, ground_truth

    def export_csv(self, records: List[Dict[str, Any]], output_path: Union[str, Path]):
        """Export records to standard CSV with JSON stringified arrays."""
        p = Path(output_path)
        p.parent.mkdir(parents=True, exist_ok=True)
        fieldnames = [
            "timestamp", "src_ip", "dst_ip", "src_port", "dst_port",
            "txid", "input_addresses", "output_addresses", "input_amounts",
            "output_amounts", "fee", "script_type", "geo_country", "asn"
        ]
        with open(p, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for r in records:
                row = dict(r)
                row["input_addresses"] = json.dumps(r["input_addresses"])
                row["output_addresses"] = json.dumps(r["output_addresses"])
                row["input_amounts"] = json.dumps(r["input_amounts"])
                row["output_amounts"] = json.dumps(r["output_amounts"])
                writer.writerow(row)

    def export_json(self, records: List[Dict[str, Any]], output_path: Union[str, Path]):
        """Export records to JSON file."""
        p = Path(output_path)
        p.parent.mkdir(parents=True, exist_ok=True)
        with open(p, "w", encoding="utf-8") as f:
            json.dump(records, f, indent=2)

    def export_ground_truth(self, ground_truth: Dict[str, Dict[str, Any]], output_path: Union[str, Path]):
        """Export isolated ground truth labels."""
        p = Path(output_path)
        p.parent.mkdir(parents=True, exist_ok=True)
        with open(p, "w", encoding="utf-8") as f:
            json.dump(ground_truth, f, indent=2)
