# TRACE Forensic Explainability & SHAP Methodology

## 1. Explainable AI via SHAP (SHapley Additive exPlanations)

In forensic intelligence, a "black box" prediction is legally and operationally unusable. Analysts must know *exactly* which behavioral signals triggered a high-priority lead.

TRACE implements SHAP TreeExplainer to decompose model probabilities into additive feature contributions based on cooperative game theory:

$$f(x) = \phi_0 + \sum_{i=1}^{M} \phi_i(x)$$

Where:
- $\phi_0$ is the base expected model probability across the training baseline.
- $\phi_i(x)$ is the marginal attribution of feature $i$ for instance $x$.
- Positive $\phi_i > 0$ denotes that the observed metric *increased* the suspicion level.
- Negative $\phi_i < 0$ denotes that the metric exerted a *normalizing / risk-mitigating* effect.

---

## 2. Multi-Layer Evidentiary Synthesis

TRACE does not rely solely on ML feature importance. It synthesizes an integrated 4-layer evidence docket:

```
+-------------------------------------------------------------------+
|                   COMBINED FORENSIC DOCKET                        |
+-------------------------------------------------------------------+
|  1. MODEL EVIDENCE:                                               |
|     - Supervised probability: 0.92                                |
|     - Isolation Forest anomaly score: 0.88                        |
|     - Top SHAP features: fan_out_ratio (+0.24), burst_score (+0.18)|
+-------------------------------------------------------------------+
|  2. NETWORK EVIDENCE:                                             |
|     - Associated relay IPs: 45.33.32.1, 185.220.101.5             |
|     - Countries: Germany (Hetzner), Netherlands (LeaseWeb)        |
|     - Observation type: P2P INV/TX message relay                  |
+-------------------------------------------------------------------+
|  3. GRAPH EVIDENCE:                                               |
|     - In-degree: 1, Out-degree: 16 (Fan-out ratio: 0.94)          |
|     - PageRank: 0.0084, Betweenness: 0.0012                       |
|     - Multi-hop path: IP -> TX1 -> Wallet_A -> TX2 -> 16 Wallets   |
+-------------------------------------------------------------------+
|  4. TRANSACTION EVIDENCE:                                         |
|     - Cumulative volume: 24.8500 BTC                              |
|     - Average transfer size: 1.5531 BTC                           |
|     - Fee rate: 12.4 sat/vB (standard priority)                   |
+-------------------------------------------------------------------+
```

---

## 3. Statutory Compliance & Non-Accusatory Framing

In compliance with criminal procedure and intelligence standards:
- All system outputs are designated as **"Investigative Leads"** or **"Behavioral Deviations"**.
- The system **never** outputs terms such as "Guilty", "Confirmed Criminal", "Proven Money Laundering", or "Definite Ownership".
- P2P relay endpoints are characterized as **"Circumstantial network broadcast observations"**, not proof of physical machine ownership or identity.
