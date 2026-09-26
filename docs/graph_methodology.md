# TRACE Graph Analytics & Link Analysis Methodology

## 1. Heterogeneous Multigraph Architecture

TRACE models Bitcoin transactions and network observations as a directed multigraph $G = (V, E)$ using NetworkX:

### Node Types ($V$)
1. **IP Node (`node_type="IP"`):** Represents a physical or cloud endpoint on the Internet broadcasting Bitcoin P2P messages. Attributes: `ip`, `country`, `asn`, `tx_count`.
2. **Wallet Node (`node_type="Wallet"`):** Represents an on-chain Bitcoin address. Attributes: `address`, `total_in`, `total_out`, `tx_count`.
3. **Transaction Node (`node_type="Transaction"`):** Represents an individual cryptographic transaction. Attributes: `txid`, `timestamp`, `amount`, `fee`, `input_count`, `output_count`.
4. **Entity Node (`node_type="Entity"`):** Represents a clustered entity resolved via Common Input Ownership. Attributes: `entity_id`, `address_count`.
5. **Cluster Node (`node_type="Cluster"`):** Represents a behavioral cohort assigned by DBSCAN.

### Edge Types ($E$)
1. **`OBSERVED` ($IP \rightarrow Transaction$):** Network layer observation linking the broadcasting node to the transaction hash.
2. **`INPUT` ($Wallet \rightarrow Transaction$):** On-chain spending script expending UTXOs.
3. **`OUTPUT` ($Transaction \rightarrow Wallet$):** On-chain payment or change output.
4. **`COMMON_INPUT` ($Wallet \leftrightarrow Wallet$):** Heuristic co-spending link between two addresses spent in the same transaction input vector.
5. **`MEMBER_OF` ($Wallet \rightarrow Entity$):** Heuristic membership edge.

---

## 2. Common Input Ownership (CIO) Heuristic

### Mathematical Formulation
The Common Input Ownership heuristic posits that if addresses $A_1, A_2, \dots, A_k$ are co-spent as inputs in a single Bitcoin transaction, they are controlled by the same private key holder or coordinating wallet software:
$$\text{If } \exists \ tx \text{ such that } \{A_1, A_2\} \subseteq \text{Inputs}(tx) \implies \text{Entity}(A_1) = \text{Entity}(A_2)$$

### Implementation via Disjoint Set Union (DSU)
TRACE implements CIO using a Disjoint Set Union data structure with path compression and rank optimization:
- Time complexity: $\mathcal{O}(\alpha(N))$ per operation (near constant time).
- Supporting transactions count tracks how many distinct transactions co-spend the address pair.
- Heuristic confidence starts at 0.75 and scales with repeated co-spending observations:
$$\text{Confidence} = \min(0.95, 0.75 + 0.05 \times N_{\text{co-spend}})$$

### Forensic Disclaimers & Caveats
The system explicitly qualifies all CIO clusters as **heuristics**:
- CoinJoin protocols, multi-signature wallets, and custodial aggregators can intentionally or coincidentally combine inputs from distinct physical entities.
- TRACE never presents CIO clusters as legally verified proof of single-person ownership.

---

## 3. Shortest Path & Evidence Chain Extraction

When an analyst investigates an alert, TRACE computes the shortest path between the observed broadcasting IP and distant destination addresses:
$$\text{Path} = [IP_A \xrightarrow{\text{OBSERVED}} TX_1 \xrightarrow{\text{OUTPUT}} W_B \xrightarrow{\text{INPUT}} TX_2 \xrightarrow{\text{OUTPUT}} W_C]$$
This walk is automatically parsed into a structured multi-layer evidentiary narrative displaying each hop, confidence score, and forensic qualification.
