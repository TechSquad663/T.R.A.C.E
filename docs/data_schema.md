# TRACE Data Schema & Ingestion Specifications

## 1. Canonical Record Structure

Every ingested record is normalized into the following standardized schema:

| Field Name | Type | Required | Description |
|:---|:---|:---|:---|
| `timestamp` | `string (ISO-8601)` | Yes | UTC timestamp of P2P network observation or block timestamp |
| `src_ip` | `string (IPv4/IPv6)` | Yes | Source IP address of node broadcasting transaction |
| `dst_ip` | `string (IPv4/IPv6)` | Yes | Destination IP address of peer receiving broadcast |
| `src_port` | `integer (1-65535)` | Yes | Source TCP port (ephemeral port) |
| `dst_port` | `integer (1-65535)` | Yes | Destination TCP port (typically 8333 for mainnet) |
| `txid` | `string (hex64)` | Yes | 64-character hexadecimal SHA256d transaction hash |
| `input_addresses` | `list[string]` | Yes | Array of spending Bitcoin addresses (base58, bech32) |
| `output_addresses`| `list[string]` | Yes | Array of recipient Bitcoin addresses |
| `input_amounts` | `list[float]` | Yes | Array of BTC amounts corresponding to input addresses |
| `output_amounts` | `list[float]` | Yes | Array of BTC amounts transferred to output addresses |
| `fee` | `float` | No | Miner fee (in BTC) |
| `script_type` | `string` | No | Script categorization (`P2PKH`, `P2SH`, `P2WPKH`, `P2TR`) |
| `geo_country` | `string` | No | ISO 2-letter country code or name |
| `asn` | `string` | No | Autonomous System Number and Organization |

---

## 2. Array Encoding Support in CSV

To accommodate diverse external data dumps, TRACE automatically handles:
- **JSON Stringified Arrays:** `["1A1zP1...", "3J98t1..."]`
- **Semicolon-Delimited Strings:** `1A1zP1...;3J98t1...`
- **Pipe-Delimited Strings:** `1A1zP1...|3J98t1...`
- **Comma-Delimited in Quoted Fields:** `"1A1zP1..., 3J98t1..."`

---

## 3. Validation Quarantine & Rejection Criteria

1. **Rejected as INVALID:**
   - Malformed TXID (not exactly 64 hexadecimal characters).
   - Negative values in input or output amounts.
   - Missing critical headers or corrupt non-parseable structures.
2. **Flagged as QUARANTINED:**
   - Unrecognized timestamp strings that cannot be resolved to UTC epoch.
   - Invalid IP address format.
   - Array length mismatches (e.g., 3 input addresses but only 2 input amounts).
3. **Flagged as DUPLICATE:**
   - Secondary occurrences of identical TXIDs within the same dataset.
