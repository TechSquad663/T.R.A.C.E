# TRACE — AI-Powered Bitcoin Transaction Traffic Forensic Intelligence Workstation

[![SIH Problem](https://img.shields.io/badge/SIH26146-Blockchain%20%26%20Cybersecurity-blue.svg)](https://www.sih.gov.in/)
[![Organization](https://img.shields.io/badge/NTRO-National%20Technical%20Research%20Organisation-red.svg)](https://ntro.gov.in)
[![Security](https://img.shields.io/badge/Air--Gapped-100%25%20Offline-success.svg)](#offline-deployment)
[![UI](https://img.shields.io/badge/GUI-PySide6%20Qt%20Native-purple.svg)](#running-the-desktop-application)
[![Tests](https://img.shields.io/badge/Tests-29%20Passed-brightgreen.svg)](#testing)

> **SIH26146:** AI-Powered Monitoring & Analysis of Bitcoin Transaction Traffic  
> **Organization:** National Technical Research Organisation (NTRO)  
> **Theme:** Blockchain & Cybersecurity  

---

## Executive Overview

**TRACE** is an air-gapped, 100% offline desktop forensic intelligence workstation developed for intelligence agencies, national security entities, and cyber-forensic analysts.

### Core Mission
In forensic investigations, law enforcement agencies encounter large volumes of captured network telemetry and blockchain transaction records. TRACE solves the core challenge of **correlating P2P network propagation observations with on-chain cryptographic settlement**, building a forensic link multigraph, and applying explainable machine learning models to identify high-priority behavioral anomalies and investigative leads—all without ever contacting an external network.

```
RAW CAPTURES (CSV/JSON/XML)
       ↓
INGESTION & QUARANTINE VALIDATION
       ↓
NETWORK ↔ BLOCKCHAIN CORRELATION
       ↓
ENTITY RESOLUTION & COMMON INPUT HEURISTIC (CIO)
       ↓
HETEROGENEOUS MULTIGRAPH (NetworkX)
       ↓
TOPOLOGICAL & CENTRALITY FEATURE SYNTHESIS
       ↓
AI / MACHINE LEARNING ENSEMBLE
├── Supervised Behavioral Detector (XGBoost)
├── Unsupervised Anomaly Detector (Isolation Forest)
└── Cohort Clustering (DBSCAN + PCA 2D)
       ↓
SHAP EXPLAINABILITY (Tree Feature Attributions)
       ↓
MULTI-SIGNAL RISK FUSION (0–100 Priority Engine)
       ↓
RANKED INVESTIGATIVE LEADS & EVIDENCE CHAIN
       ↓
PYSIDE6 NATIVE DESKTOP CONSOLE & 12-SECTION PDF REPORT
```

---

## Key Features

1. **100% Offline & Air-Gap Verified:** Zero external API calls, zero web trackers, zero runtime package downloads. Includes an automated socket verification guard (`scripts/verify_offline.py`).
2. **Multi-Format Ingestion:** Robust ingestion of CSV, JSON, and XML files with automatic delimiter sniffing, array parsing, and schema quarantine.
3. **Cross-Layer Correlation:** Cryptographic matching of network P2P broadcast events (`src_ip`, `dst_ip`, `port`, `asn`) with on-chain Bitcoin ledger transactions (`txid`, inputs, outputs, fee).
4. **Common Input Ownership (CIO) Heuristic:** Disjoint Set Union (Union-Find) clustering to group co-spent input addresses into provisional entities with confidence calibration.
5. **Heterogeneous Graph Analytics:** Full NetworkX multigraph supporting degree centrality, PageRank, betweenness centrality, and shortest evidence path generation.
6. **Triple-Engine AI/ML:**
   - **XGBoost:** Primary supervised detector classifying behavioral patterns.
   - **Isolation Forest:** Secondary unsupervised multivariate anomaly detector.
   - **DBSCAN:** Behavioral cohort clustering with 2D PCA projection.
7. **Explainability via SHAP:** Generates additive feature attributions for every flagged lead, highlighting exactly which behavioral traits elevated risk.
8. **Statutory Evidentiary Language:** Strictly adheres to forensic standards—presents findings as *"Investigative Leads"*, *"Anomalous Behaviors"*, and *"Circumstantial Relay Observations"*, never fabricating legal guilt.
9. **Interactive Link Analysis Canvas:** Native PySide6 `QGraphicsView` graph visualizer featuring zoom, pan, 1-hop/2-hop neighborhood expansion, and evidence chain tracing.
10. **Official 12-Section PDF Lead Reports:** Generates law-enforcement-ready PDF dossiers and CSV/JSON data extracts offline.

---

## Technology Stack

- **GUI Framework:** PySide6 (Qt for Python 6.11+)
- **Data Engineering:** DuckDB, Polars, Pandas, NumPy
- **Graph Analytics:** NetworkX
- **Machine Learning:** XGBoost, Scikit-Learn, Joblib
- **Forensic Explainability:** SHAP (SHapley Additive exPlanations)
- **Document Generation:** ReportLab
- **Testing & Verification:** PyTest

---

## Installation & Setup

### Requirements
- **OS:** Linux (Ubuntu 22.04+, Debian 12+, RHEL 9+) or Windows 10/11
- **Python:** Python 3.11+

### Quick Start (Local Environment)

```bash
# 1. Clone repository
git clone https://github.com/ntro-sih/TRACE.git
cd TRACE

# 2. Create virtual environment
python -m venv .venv

# 3. Activate virtual environment
# Linux:
source .venv/bin/activate
# Windows:
.venv\Scripts\activate

# 4. Install dependencies
pip install -r requirements.txt
```

---

## Running the Desktop Application

Launch the native PySide6 workstation with:

```bash
python main.py
```

### The 10-Step Hackathon Judge Demonstration Flow

1. **Launch:** Run `python main.py`. Note the green **`🛡️ OFFLINE VERIFIED`** indicator in the header.
2. **Generate Demo Data:** Click **`[⚡ Run Demo Investigation]`** in the header or overview page.
3. **Automated Pipeline Execution:** Watch the 14-stage background worker process 1,200 transactions across 10 behavioral archetypes.
4. **Overview Dashboard:** Review dataset KPIs, risk distribution breakdown, and topological metrics.
5. **Triage Leads:** Navigate to **Ranked Alerts** (`ui/alerts`). Open the highest-priority lead.
6. **Examine "Why Flagged":** Review the **SHAP feature attribution waterfall** showing the exact behavioral drivers (e.g. `fan_out_ratio: +0.28`, `burst_score: +0.19`).
7. **Link Analysis:** Open **Link Analysis** (`ui/graph`). Click on the flagged entity and click **`[1-Hop Neighborhood]`** or **`[2-Hop Neighborhood]`** to visually isolate the fund dispersion tree.
8. **Trace Evidence Chain:** Open **Evidence Chain** (`ui/evidence`) to review the multi-layer step-by-step causal chain (`IP -> TX -> Wallet -> Destination Wallet`).
9. **Export PDF Dossier:** Navigate to **Reports & Exports** (`ui/reports`) and click **`[📑 Generate Official PDF Lead Report]`**. View the generated 12-section PDF in `data/exports/`.
10. **Offline Proof:** Disconnect Wi-Fi and Ethernet. Rerun `python scripts/verify_offline.py`—100% of pipeline stages execute with zero network calls!

---

## Command-Line Scripts

| Script | Purpose | Example Command |
|:---|:---|:---|
| `scripts/verify_offline.py` | Audits air-gap integrity and socket blocks | `python scripts/verify_offline.py` |
| `scripts/generate_dataset.py` | Generates realistic synthetic Bitcoin datasets | `python scripts/generate_dataset.py --rows 2000 --seed 42` |
| `scripts/train_models.py` | Trains and persists offline ML models | `python scripts/train_models.py` |
| `scripts/run_pipeline.py` | CLI investigation pipeline on any dataset | `python scripts/run_pipeline.py data/synthetic/sample.csv --export-pdf` |
| `scripts/evaluate_models.py` | Evaluates holdout and distribution-shift metrics | `python scripts/evaluate_models.py` |

---

## Testing

Execute the comprehensive 29-test unit and security suite:

```bash
pytest tests/ -v
```

All 29 tests validate:
- CSV, JSON, XML ingestion and malformed data handling.
- TXID validation, IP checks, array mismatch quarantines.
- Disjoint Set Union (DSU) and Common Input Ownership (CIO).
- Heterogeneous graph construction and centrality algorithms.
- Zero ground-truth leakage into ML feature columns.
- XGBoost, Isolation Forest, and SHAP explainability.
- Strict socket lockdown and offline air-gap enforcement.

---

## Offline Deployment & Packaging

To package TRACE for deployment onto a completely isolated, air-gapped Linux or Windows machine without Internet access:

```bash
# On Internet-connected staging machine:
pip download -d wheels -r requirements.txt

# Transfer TRACE/ directory and wheels/ to air-gapped machine, then:
pip install --no-index --find-links=wheels -r requirements.txt
```

---

## Forensic Limitations & Compliance

- **Synthetic Modeling:** Datasets are synthetic models adhering to real Bitcoin P2P and ledger specifications. They do not contain seized real-world live traffic.
- **Relay Observation vs. Ownership:** An observed source IP reflects a P2P gossip relay hop, not verified physical wallet ownership.
- **Heuristic Nature of CIO:** Common Input Ownership is a heuristic subject to CoinJoin/mixing caveats.
- **Investigative Leads:** All flagged alerts represent analytical triage signals requiring manual analyst corroboration before enforcement actions.

---

## License

MIT License. Copyright (c) 2026 TRACE Project Contributors (SIH26146 - NTRO).
