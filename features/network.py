"""Network-layer observation features (IP diversity, geo dispersion, ASN diversity)."""
from typing import List, Dict, Any


def extract_network_features(observations: List[Dict[str, Any]]) -> Dict[str, float]:
    """Compute network-layer behavioral metrics."""
    if not observations:
        return {
            "unique_source_ips": 0.0,
            "unique_dest_ips": 0.0,
            "unique_countries": 0.0,
            "unique_asns": 0.0,
            "ip_reuse_rate": 0.0,
            "port_diversity": 0.0,
        }

    src_ips = set()
    dst_ips = set()
    countries = set()
    asns = set()
    ports = set()

    for obs in observations:
        if obs.get("src_ip"):
            src_ips.add(obs["src_ip"])
        if obs.get("dst_ip"):
            dst_ips.add(obs["dst_ip"])
        if obs.get("geo_country") and obs["geo_country"] != "Unknown":
            countries.add(obs["geo_country"])
        if obs.get("asn") and obs["asn"] != "Unknown":
            asns.add(obs["asn"])
        if obs.get("src_port"):
            ports.add(obs["src_port"])

    tot_obs = len(observations)
    ip_reuse_rate = tot_obs / max(1.0, float(len(src_ips)))

    return {
        "unique_source_ips": float(len(src_ips)),
        "unique_dest_ips": float(len(dst_ips)),
        "unique_countries": float(len(countries)),
        "unique_asns": float(len(asns)),
        "ip_reuse_rate": round(ip_reuse_rate, 3),
        "port_diversity": float(len(ports)),
    }
