# TRACE Offline Air-Gapped Deployment Guide

## 1. Air-Gapped Deployment Overview

TRACE is built to operate in SCIF (Sensitive Compartmented Information Facility) and high-security air-gapped environments where outbound Internet access is physically disconnected.

---

## 2. Preparing Offline Wheelhouse (Connected Staging Machine)

On an internet-connected staging machine with Python 3.11+:

```bash
# 1. Clone repository
git clone https://github.com/ntro-sih/TRACE.git
cd TRACE

# 2. Download all wheels locally
mkdir wheels
pip download -d wheels -r requirements.txt
```

---

## 3. Installing on Air-Gapped Target Machine (Linux / Windows)

Transfer the project directory and `wheels/` folder to the air-gapped target workstation via authorized optical media or encrypted drive:

```bash
# 1. Create local virtual environment
python -m venv .venv

# 2. Activate virtual environment
# Linux:
source .venv/bin/activate
# Windows:
.venv\Scripts\activate

# 3. Install packages strictly from local wheels (ZERO network access)
pip install --no-index --find-links=wheels -r requirements.txt
```

---

## 4. Running the Offline Verification Audit

Before initiating intelligence operations, execute the automated socket audit:

```bash
python scripts/verify_offline.py
```

This script:
1. Injects a monkey-patch into the Python `socket` module blocking all non-loopback outbound connections.
2. Ingests and validates metadata records.
3. Constructs the NetworkX graph and runs feature synthesis.
4. Executes XGBoost, Isolation Forest, and DBSCAN clustering.
5. Generates SHAP explainability matrices.
6. Renders a complete 12-section PDF lead report.
7. Confirms that ZERO outbound socket calls were attempted.

---

## 5. Launching the Workstation

```bash
python main.py
```

The application window will open with the **"🛡️ OFFLINE VERIFIED"** badge displayed in the header and status bar.
