"""Canonical schemas and validation rules for TRACE."""
from typing import Dict, Any, List

CANONICAL_SCHEMA: Dict[str, Dict[str, Any]] = {
    "timestamp": {
        "type": "datetime",
        "required": True,
        "description": "ISO-8601 or UNIX epoch timestamp of the network observation or transaction confirmation",
    },
    "src_ip": {
        "type": "ipv4_or_ipv6",
        "required": True,
        "description": "Source IP address of the P2P node relaying the transaction message",
    },
    "dst_ip": {
        "type": "ipv4_or_ipv6",
        "required": True,
        "description": "Destination IP address of the receiving Bitcoin node",
    },
    "src_port": {
        "type": "integer",
        "required": True,
        "min": 1,
        "max": 65535,
        "default": 8333,
        "description": "TCP port on the source host",
    },
    "dst_port": {
        "type": "integer",
        "required": True,
        "min": 1,
        "max": 65535,
        "default": 8333,
        "description": "TCP port on the destination node (typically 8333)",
    },
    "txid": {
        "type": "hex64",
        "required": True,
        "description": "64-character hexadecimal Bitcoin transaction hash (SHA256d)",
    },
    "input_addresses": {
        "type": "array_of_strings",
        "required": True,
        "description": "List of Bitcoin input/spending addresses (base58, bech32)",
    },
    "output_addresses": {
        "type": "array_of_strings",
        "required": True,
        "description": "List of Bitcoin recipient/destination addresses",
    },
    "input_amounts": {
        "type": "array_of_floats",
        "required": True,
        "description": "List of input amounts (BTC or satoshis)",
    },
    "output_amounts": {
        "type": "array_of_floats",
        "required": True,
        "description": "List of output amounts (BTC or satoshis)",
    },
    "geo_country": {
        "type": "string",
        "required": False,
        "default": "Unknown",
        "description": "ISO 2-letter country code or country name of the source node",
    },
    "asn": {
        "type": "string",
        "required": False,
        "default": "Unknown",
        "description": "Autonomous System Number (e.g., AS15169)",
    },
    "fee": {
        "type": "float",
        "required": False,
        "default": 0.0,
        "description": "Transaction fee paid to miners",
    },
    "script_type": {
        "type": "string",
        "required": False,
        "default": "P2PKH",
        "description": "Primary script type (P2PKH, P2SH, P2WPKH, P2WSH, P2TR)",
    }
}
