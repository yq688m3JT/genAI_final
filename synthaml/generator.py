"""Synthetic transaction generation for SynthAML."""

from __future__ import annotations

import random
from datetime import datetime, timedelta

import numpy as np
import pandas as pd

from .typology import TypologyConfig


CURRENCIES = ["USD", "EUR", "GBP", "SGD", "HKD"]
LEGIT_NARRATIVES = [
    "monthly supplier payment",
    "payroll batch",
    "platform settlement",
    "shipping invoice",
    "software subscription",
    "tax remittance",
]


def generate_guided_transactions(
    config: TypologyConfig,
    n_records: int = 250,
    suspicious_ratio: float = 0.18,
    seed: int = 42,
) -> pd.DataFrame:
    """Generate typology-guided synthetic transactions.

    Suspicious transactions are generated as small chains: one funding transfer
    followed by several outgoing split transfers within a short time window.
    """

    rng = random.Random(seed)
    np_rng = np.random.default_rng(seed)
    n_records = max(50, int(n_records))
    suspicious_target = max(8, int(n_records * suspicious_ratio))

    rows: list[dict] = []
    base_time = datetime(2026, 1, 5, 9, 0, 0)
    account_pool = _account_pool(rng, 55)

    suspicious_count = 0
    while suspicious_count < suspicious_target:
        chain = _make_suspicious_chain(config, rng, base_time, account_pool)
        if suspicious_count + len(chain) > suspicious_target + config.split_count_max:
            break
        rows.extend(chain)
        suspicious_count += len(chain)

    while len(rows) < n_records:
        rows.append(_make_legit_transaction(config, rng, np_rng, base_time, account_pool))

    if len(rows) > n_records:
        complete_chains = {row["chain_id"] for row in rows if row["chain_id"]}
        protected = [row for row in rows if row["chain_id"] in complete_chains]
        legit = [row for row in rows if not row["chain_id"]]
        rows = protected + legit[: max(0, n_records - len(protected))]
    rng.shuffle(rows)
    frame = pd.DataFrame(rows)
    frame["timestamp"] = pd.to_datetime(frame["timestamp"])
    frame = frame.sort_values("timestamp").reset_index(drop=True)
    frame["tx_id"] = [f"TX-{i + 1:06d}" for i in range(len(frame))]
    return frame[
        [
            "tx_id",
            "timestamp",
            "sender_account",
            "receiver_account",
            "origin_region",
            "destination_region",
            "amount",
            "currency",
            "narrative",
            "channel",
            "chain_id",
            "risk_signal",
            "label",
        ]
    ]


def generate_rule_baseline(
    config: TypologyConfig,
    n_records: int = 250,
    suspicious_ratio: float = 0.18,
    seed: int = 42,
) -> pd.DataFrame:
    """Generate a simpler amount-threshold baseline dataset."""

    rng = random.Random(seed)
    np_rng = np.random.default_rng(seed)
    rows = []
    base_time = datetime(2026, 1, 5, 9, 0, 0)
    account_pool = _account_pool(rng, 55)
    suspicious_target = max(8, int(n_records * suspicious_ratio))

    for idx in range(n_records):
        is_suspicious = idx < suspicious_target
        sender, receiver = rng.sample(account_pool, 2)
        amount = (
            rng.uniform(config.amount_max * 0.82, config.amount_max * 1.05)
            if is_suspicious
            else float(np_rng.lognormal(mean=8.2, sigma=0.8))
        )
        rows.append(
            {
                "tx_id": f"RB-{idx + 1:06d}",
                "timestamp": base_time + timedelta(hours=rng.randint(0, 24 * 21)),
                "sender_account": sender,
                "receiver_account": receiver,
                "origin_region": rng.choice(config.origin_regions),
                "destination_region": rng.choice(config.destination_regions),
                "amount": round(min(amount, config.amount_max * 1.2), 2),
                "currency": rng.choice(CURRENCIES),
                "narrative": rng.choice(LEGIT_NARRATIVES),
                "channel": rng.choice(["wire", "ach", "card", "wallet"]),
                "chain_id": f"RULE-{idx + 1:04d}" if is_suspicious else "",
                "risk_signal": "large transfer threshold" if is_suspicious else "none",
                "label": "suspicious" if is_suspicious else "legitimate",
            }
        )

    frame = pd.DataFrame(rows).sort_values("timestamp").reset_index(drop=True)
    return frame


def _account_pool(rng: random.Random, size: int) -> list[str]:
    prefixes = ["ALPHA", "BRIDGE", "CROWN", "DELTA", "EAST", "NOVA"]
    return [f"{rng.choice(prefixes)}-{rng.randint(10000, 99999)}" for _ in range(size)]


def _make_suspicious_chain(
    config: TypologyConfig,
    rng: random.Random,
    base_time: datetime,
    account_pool: list[str],
) -> list[dict]:
    chain_id = f"CHAIN-{rng.getrandbits(32):08X}"
    hub = rng.choice(account_pool)
    funder = f"SHELL-{rng.randint(10000, 99999)}"
    splits = rng.randint(config.split_count_min, config.split_count_max)
    total = rng.uniform(config.amount_min * splits, config.amount_max)
    start = base_time + timedelta(days=rng.randint(0, 20), hours=rng.randint(7, 19))

    rows = [
        {
            "timestamp": start,
            "sender_account": funder,
            "receiver_account": hub,
            "origin_region": rng.choice(config.origin_regions),
            "destination_region": rng.choice(config.origin_regions),
            "amount": round(total, 2),
            "currency": rng.choice(CURRENCIES),
            "narrative": rng.choice(config.narrative_terms),
            "channel": rng.choice(["wire", "wallet"]),
            "chain_id": chain_id,
            "risk_signal": "funding transfer before rapid split",
            "label": "suspicious",
        }
    ]

    remaining = total
    for split_idx in range(splits):
        if split_idx == splits - 1 or remaining < config.amount_min * 0.35:
            amount = remaining
        else:
            amount = min(max(config.amount_min * 0.35, total * rng.uniform(0.08, 0.28)), remaining)
        remaining -= amount
        rows.append(
            {
                "timestamp": start + timedelta(hours=rng.randint(1, config.time_window_hours)),
                "sender_account": hub,
                "receiver_account": f"CP-{rng.randint(10000, 99999)}",
                "origin_region": rng.choice(config.origin_regions),
                "destination_region": rng.choice(config.destination_regions),
                "amount": round(amount, 2),
                "currency": rng.choice(CURRENCIES),
                "narrative": rng.choice(config.narrative_terms),
                "channel": rng.choice(["wire", "wallet", "ach"]),
                "chain_id": chain_id,
                "risk_signal": rng.choice(config.suspicious_methods),
                "label": "suspicious",
            }
        )

    return rows


def _make_legit_transaction(
    config: TypologyConfig,
    rng: random.Random,
    np_rng: np.random.Generator,
    base_time: datetime,
    account_pool: list[str],
) -> dict:
    sender, receiver = rng.sample(account_pool, 2)
    amount = float(np_rng.lognormal(mean=8.0, sigma=0.9))
    return {
        "timestamp": base_time + timedelta(days=rng.randint(0, 24), hours=rng.randint(6, 20)),
        "sender_account": sender,
        "receiver_account": receiver,
        "origin_region": rng.choice(config.origin_regions),
        "destination_region": rng.choice(config.destination_regions + config.origin_regions),
        "amount": round(min(amount, config.amount_max * 0.75), 2),
        "currency": rng.choice(CURRENCIES),
        "narrative": rng.choice(LEGIT_NARRATIVES),
        "channel": rng.choice(["wire", "ach", "card", "wallet"]),
        "chain_id": "",
        "risk_signal": "none",
        "label": "legitimate",
    }
