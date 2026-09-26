"""Generates human-readable, non-accusatory forensic explanation narratives."""
from typing import Dict, Any, List


class ExplanationGenerator:
    """Produces structured evidentiary narratives conforming strictly to statutory forensic standards."""

    @staticmethod
    def generate_narrative(evidence_docket: Dict[str, Any]) -> str:
        """Format a clear, analytical investigation briefing for an intelligence analyst."""
        ent_id = evidence_docket.get("entity_id", "Unknown")
        risk = evidence_docket.get("risk_score", 0.0)
        priority = evidence_docket.get("priority", "Low")
        model_prob = evidence_docket.get("model_probability", 0.0)
        anomaly = evidence_docket.get("anomaly_score", 0.0)
        reasons = evidence_docket.get("reasons", [])
        features = evidence_docket.get("top_contributing_features", [])
        ips = evidence_docket.get("associated_ips", [])

        lines = [
            f"=== INVESTIGATIVE LEAD DOSSIER: {ent_id} ===",
            f"PRIORITY CLASSIFICATION: {priority.upper()}",
            f"RISK INDICATOR: {risk}/100 | CONFIDENCE: {int(evidence_docket.get('confidence', 0.8) * 100)}%",
            "",
            "1. EXECUTIVE ANALYTICAL SUMMARY",
            f"Entity '{ent_id}' was flagged for forensic review based on behavioral deviation and statistical anomalies.",
            "This finding constitutes an investigative lead for further corroboration and does NOT represent verified criminality.",
            "",
            "2. PRIMARY RISK SIGNALS",
        ]

        for r in reasons:
            lines.append(f"  • {r}")

        lines.extend([
            "",
            "3. AI/ML MODEL & ANOMALY ATTRIBUTION",
            f"  • Supervised Model Probability: {model_prob:.2f} (Pattern alignment with behavioral anomaly archetypes)",
            f"  • Isolation Forest Anomaly Score: {anomaly:.2f} (Multivariate deviation from population baseline)",
            "",
            "Key Behavioral Feature Drivers:",
        ])

        for f in features[:5]:
            fname = f.get("feature", "")
            imp = f.get("impact", 0.0)
            val = f.get("value", 0.0)
            desc = f.get("description", "")
            direction = f.get("direction", "")
            lines.append(f"  • {fname} (value: {val:.2f}, impact: {imp:+.3f}) -> {desc}")

        lines.extend([
            "",
            "4. NETWORK & TOPOLOGICAL CORROBORATION",
            f"  • Associated P2P Broadcast IPs: {len(ips)} distinct endpoints ({', '.join(ips[:3]) if ips else 'None recorded'})",
            f"  • Transaction Volume: {evidence_docket.get('transaction_count', 0)} transactions recorded",
            f"  • Total Flow: {evidence_docket.get('total_out_btc', 0.0):.4f} BTC out / {evidence_docket.get('total_in_btc', 0.0):.4f} BTC in",
            f"  • Flow Asymmetry: Fan-Out={evidence_docket.get('fan_out_ratio', 0.0):.2f}, Fan-In={evidence_docket.get('fan_in_ratio', 0.0):.2f}",
            "",
            "5. FORENSIC QUALIFICATION & LIMITATIONS",
            "  * Network IP associations represent circumstantial P2P relay observations, not verified wallet ownership.",
            "  * Multi-input grouping (if present) is heuristic (Common-Input Ownership) and subject to CoinJoin/mixing caveats.",
        ])

        return "\n".join(lines)
