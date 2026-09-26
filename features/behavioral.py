"""Wallet and entity behavioral profile feature extraction."""
import math
from typing import List, Dict, Any
from core.models import TransactionRecord


def extract_wallet_behavioral_features(
    entity_addresses: List[str],
    entity_records: List[TransactionRecord],
) -> Dict[str, float]:
    """Compute aggregate statistical and behavioral metrics for a wallet or entity."""
    if not entity_records:
        return {
            "tx_count": 0.0,
            "total_in": 0.0,
            "total_out": 0.0,
            "avg_amount": 0.0,
            "max_amount": 0.0,
            "std_amount": 0.0,
            "unique_counterparties": 0.0,
            "fan_in_ratio": 0.0,
            "fan_out_ratio": 0.0,
        }

    addr_set = set(entity_addresses)
    amounts: List[float] = []
    counterparties = set()
    in_transfers = 0
    out_transfers = 0

    tot_in = 0.0
    tot_out = 0.0
    peeling_chain_count = 0

    for r in entity_records:
        # Check inputs
        has_entity_input = False
        for idx, in_addr in enumerate(r.input_addresses):
            amt = r.input_amounts[idx] if idx < len(r.input_amounts) else 0.0
            if in_addr in addr_set:
                has_entity_input = True
                tot_out += amt
                out_transfers += 1
                amounts.append(amt)
                for out_addr in r.output_addresses:
                    if out_addr not in addr_set:
                        counterparties.add(out_addr)

        # Peeling chain detection heuristic
        # Condition: Entity spends input, has exactly 2 outputs, one small payment outside, one large change inside.
        if has_entity_input and len(r.output_addresses) == 2:
            out_0_in_entity = r.output_addresses[0] in addr_set
            out_1_in_entity = r.output_addresses[1] in addr_set
            
            # Exactly one output goes back to entity (change), one goes outside (payment)
            if out_0_in_entity != out_1_in_entity:
                amt_0 = r.output_amounts[0] if len(r.output_amounts) > 0 else 0
                amt_1 = r.output_amounts[1] if len(r.output_amounts) > 1 else 0
                
                if out_0_in_entity and amt_0 > amt_1 * 5:  # Change is significantly larger than payment
                    peeling_chain_count += 1
                elif out_1_in_entity and amt_1 > amt_0 * 5:
                    peeling_chain_count += 1

        # Check outputs
        for idx, out_addr in enumerate(r.output_addresses):
            amt = r.output_amounts[idx] if idx < len(r.output_amounts) else 0.0
            if out_addr in addr_set:
                tot_in += amt
                in_transfers += 1
                amounts.append(amt)
                for in_addr in r.input_addresses:
                    if in_addr not in addr_set:
                        counterparties.add(in_addr)

    tx_count = len(entity_records)
    avg_amt = sum(amounts) / max(1, len(amounts)) if amounts else 0.0
    max_amt = max(amounts) if amounts else 0.0

    if len(amounts) > 1:
        variance = sum((x - avg_amt) ** 2 for x in amounts) / len(amounts)
        std_amt = math.sqrt(variance)
    else:
        std_amt = 0.0

    tot_transfers = max(1, in_transfers + out_transfers)
    fan_in_ratio = in_transfers / tot_transfers
    fan_out_ratio = out_transfers / tot_transfers

    return {
        "tx_count": float(tx_count),
        "total_in": round(tot_in, 6),
        "total_out": round(tot_out, 6),
        "avg_amount": round(avg_amt, 6),
        "max_amount": round(max_amt, 6),
        "std_amount": round(std_amt, 6),
        "unique_counterparties": float(len(counterparties)),
        "fan_in_ratio": round(fan_in_ratio, 4),
        "fan_out_ratio": round(fan_out_ratio, 4),
        "peeling_chain_count": float(peeling_chain_count),
    }
