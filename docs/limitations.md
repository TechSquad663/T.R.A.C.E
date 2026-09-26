# TRACE Forensic Limitations & Analytical Boundaries

## 1. Synthetic Telemetry vs. Live Intercept Data

The datasets processed by TRACE are synthetic telemetry modeled on real Bitcoin protocol and network packet formats. They do not constitute seized real-world criminal evidence or physical wiretap captures.

---

## 2. Network Layer Ambiguities

1. **P2P Relay Propagation:**
   - In the Bitcoin peer-to-peer gossip network, nodes relay transactions that they did not originate.
   - An observed source IP (`src_ip`) represents an intermediary relay hop; it **does not** prove that the host machine controls the private key or initiated the transaction.
2. **Proxies, VPNs, and Anonymity Networks:**
   - Nodes operating over Tor, I2P, or VPN endpoints mask the true originating physical topology.
   - TRACE flags multi-IP associations as circumstantial indicators for analyst review, never as identity proof.

---

## 3. Blockchain Layer Heuristic Boundaries

1. **Common Input Ownership (CIO) Caveats:**
   - While multi-input transactions often reflect single-wallet consolidation, CoinJoin protocols (Wasabi, Whirlpool) intentionally mix inputs from distinct unrelated users.
   - Exchange hot wallets routinely aggregate deposits from multiple customers into massive multi-input sweeps.
   - CIO is treated strictly as a **heuristic indicator**.
2. **Change Address Ambiguity:**
   - Discerning which output is payment versus change requires heuristics (address reuse, script type matching, round amounts) that carry non-zero false positive rates.

---

## 4. Evidentiary Standards

TRACE outputs are **Investigative Leads (Triage Signals)** designed to assist intelligence analysts in prioritizing large metadata volumes. Every finding requires corroboration through subpoenas, exchange KYC disclosures, and digital device forensics.
