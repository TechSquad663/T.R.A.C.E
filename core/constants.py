"""Constants and compliance definitions for TRACE."""

# Canonical dataset column names
CANONICAL_FIELDS = [
    "timestamp",
    "src_ip",
    "dst_ip",
    "src_port",
    "dst_port",
    "txid",
    "input_addresses",
    "output_addresses",
    "input_amounts",
    "output_amounts",
    "geo_country",
    "asn",
]

# Extended forensic fields
OPTIONAL_FIELDS = [
    "fee",
    "script_type",
    "tx_size_bytes",
    "protocol_version",
    "user_agent",
]

# Default Bitcoin network parameters
DEFAULT_BITCOIN_PORT = 8333
DEFAULT_BITCOIN_TESTNET_PORT = 18333

# Semantic Color Codes (Dark workstation palette)
RISK_COLORS = {
    "Critical": "#EF4444",      # Red-500
    "High": "#F97316",          # Orange-500
    "Medium": "#EAB308",        # Yellow-500
    "Low": "#10B981",           # Emerald-500
    "Informational": "#3B82F6",  # Blue-500
}

NODE_COLORS = {
    "IP": "#38BDF8",            # Sky Blue
    "Wallet": "#A855F7",        # Purple
    "Transaction": "#F59E0B",   # Amber
    "Entity": "#EC4899",        # Pink
    "Cluster": "#06B6D4",       # Cyan
}

EDGE_COLORS = {
    "OBSERVED": "#38BDF8",
    "INPUT": "#A855F7",
    "OUTPUT": "#F59E0B",
    "COMMON_INPUT": "#EC4899",
    "TRANSFER": "#10B981",
    "ASSOCIATED": "#64748B",
    "MEMBER_OF": "#06B6D4",
}

# Forensic Status & Non-Accusatory Descriptions
STATUS_DESCRIPTIONS = {
    "CIO_HEURISTIC": "Probable common-input entity (Multi-input clustering heuristic; does not represent legally verified ownership)",
    "IP_CORRELATION": "Network observation linked to transaction (P2P relay observation; does not confirm wallet ownership or transaction origination)",
    "INVESTIGATIVE_LEAD": "Investigative lead flagged for review based on behavioral deviation and statistical anomalies",
    "ANOMALY_FLAG": "Anomalous behavior detected relative to standard baseline traffic distributions",
}

DISCLAIMER_TEXT = (
    "LEGAL & FORENSIC COMPLIANCE NOTICE: TRACE is an offline intelligence workstation designed for analytical "
    "triage and lead generation. In compliance with evidentiary standards, correlations between network observations (IPs) "
    "and blockchain records (wallets/transactions) represent contextual observational evidence rather than verified physical identity. "
    "Common-input clustering is a heuristic. All flagged items represent investigative leads requiring manual analyst corroboration."
)
