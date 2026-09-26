"""Explainable multi-signal risk fusion engine."""
import logging
from typing import Dict, Any, List, Optional
from config.settings import get_settings

logger = logging.getLogger("TRACE.RiskEngine")


class RiskEngine:
    """Fuses supervised ML, unsupervised anomaly scores, graph topology, and network dispersion into an internal 0-100 risk indicator."""

    def __init__(
        self,
        weight_model: Optional[float] = None,
        weight_anomaly: Optional[float] = None,
        weight_graph: Optional[float] = None,
        weight_network: Optional[float] = None,
    ):
        settings = get_settings()
        self.w_model = weight_model if weight_model is not None else settings.WEIGHT_MODEL_PROB
        self.w_anomaly = weight_anomaly if weight_anomaly is not None else settings.WEIGHT_ANOMALY_SCORE
        self.w_graph = weight_graph if weight_graph is not None else settings.WEIGHT_GRAPH_SIGNAL
        self.w_network = weight_network if weight_network is not None else settings.WEIGHT_NETWORK_SIGNAL

        # Normalize weights if sum != 1.0
        total_w = self.w_model + self.w_anomaly + self.w_graph + self.w_network
        if total_w > 0:
            self.w_model /= total_w
            self.w_anomaly /= total_w
            self.w_graph /= total_w
            self.w_network /= total_w

    def compute_graph_signal(self, graph_features: Dict[str, float]) -> float:
        """Derive normalized 0-1 graph signal from centrality and topology."""
        fan_out = min(1.0, float(graph_features.get("graph_fan_out_ratio", 0.0)))
        fan_in = min(1.0, float(graph_features.get("graph_fan_in_ratio", 0.0)))
        pagerank = min(1.0, float(graph_features.get("graph_pagerank", 0.0)) * 50.0)
        betweenness = min(1.0, float(graph_features.get("graph_betweenness", 0.0)) * 20.0)

        # High fan-out or fan-in with significant centrality elevates graph signal
        extreme_flow = max(fan_out, fan_in)
        signal = (0.5 * extreme_flow) + (0.3 * pagerank) + (0.2 * betweenness)
        return min(1.0, max(0.0, float(signal)))

    def compute_network_signal(self, network_features: Dict[str, float]) -> float:
        """Derive normalized 0-1 network signal from IP and geographic dispersion."""
        ips = float(network_features.get("unique_source_ips", 1.0))
        countries = float(network_features.get("unique_countries", 1.0))
        asns = float(network_features.get("unique_asns", 1.0))

        # Scoring heuristics: multi-IP (>3) and multi-country (>2) elevate network suspicion
        ip_score = min(1.0, max(0.0, (ips - 1.0) / 4.0))
        country_score = min(1.0, max(0.0, (countries - 1.0) / 3.0))
        asn_score = min(1.0, max(0.0, (asns - 1.0) / 3.0))

        signal = (0.45 * ip_score) + (0.35 * country_score) + (0.20 * asn_score)
        return min(1.0, max(0.0, float(signal)))

    def evaluate_risk(
        self,
        model_prob: float,
        anomaly_score: float,
        graph_signal: float,
        network_signal: float,
        raw_features: Optional[Dict[str, float]] = None,
    ) -> Dict[str, Any]:
        """
        Synthesize signals into a 0-100 risk score with qualitative justification reasons.
        """
        m_p = min(1.0, max(0.0, float(model_prob)))
        a_s = min(1.0, max(0.0, float(anomaly_score)))
        g_s = min(1.0, max(0.0, float(graph_signal)))
        n_s = min(1.0, max(0.0, float(network_signal)))

        fused_score = (
            (self.w_model * m_p) +
            (self.w_anomaly * a_s) +
            (self.w_graph * g_s) +
            (self.w_network * n_s)
        ) * 100.0

        risk_score = round(fused_score, 1)

        # Generate contextual justification reasons
        reasons: List[str] = []
        if m_p >= 0.70:
            reasons.append(f"High supervised model probability ({m_p:.2f}) aligning with known behavioral patterns")
        if a_s >= 0.75:
            reasons.append(f"Statistically anomalous behavioral profile ({a_s:.2f}) diverging from population baseline")
        if g_s >= 0.60:
            reasons.append(f"Elevated graph topological prominence (graph signal: {g_s:.2f}) with asymmetric flow ratios")
        if n_s >= 0.50:
            reasons.append(f"Circumstantial network dispersion across multiple nodes/jurisdictions (network signal: {n_s:.2f})")

        if raw_features:
            if raw_features.get("fan_out_ratio", 0.0) >= 0.70:
                reasons.append("Unusually high fan-out fund dispersion")
            if raw_features.get("fan_in_ratio", 0.0) >= 0.70:
                reasons.append("High fan-in consolidation from multiple inputs")
            if raw_features.get("burst_score", 0.0) >= 0.60:
                reasons.append("Marked temporal burstiness in transaction dispatching")
            if raw_features.get("unique_source_ips", 0.0) >= 3:
                reasons.append("Multi-IP association observed during relay propagation")

        if not reasons:
            reasons.append("Baseline behavioral characteristics within standard operational parameters")

        return {
            "risk_score": risk_score,
            "model_probability": round(m_p, 4),
            "anomaly_score": round(a_s, 4),
            "graph_signal": round(g_s, 4),
            "network_signal": round(n_s, 4),
            "reasons": reasons,
            "weights": {
                "model_prob": round(self.w_model, 2),
                "anomaly": round(self.w_anomaly, 2),
                "graph": round(self.w_graph, 2),
                "network": round(self.w_network, 2),
            },
        }
