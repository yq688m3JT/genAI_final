"""Evaluation utilities for SynthAML."""

from __future__ import annotations

import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import f1_score, precision_score, recall_score
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline

from .generator import generate_guided_transactions, generate_rule_baseline
from .typology import TypologyConfig


def evaluate_generators(config: TypologyConfig, n_records: int = 500, seed: int = 7) -> dict:
    """Compare guided synthetic data with the simpler rule baseline."""

    guided = generate_guided_transactions(config, n_records=n_records, seed=seed)
    baseline = generate_rule_baseline(config, n_records=n_records, seed=seed)
    hidden = generate_guided_transactions(config, n_records=n_records, seed=seed + 99)

    guided_metrics = _score_transfer(guided, hidden, seed)
    baseline_metrics = _score_transfer(baseline, hidden, seed)

    return {
        "guided": guided_metrics,
        "baseline": baseline_metrics,
        "guided_records": len(guided),
        "baseline_records": len(baseline),
        "rubric": {
            "good_output": [
                "suspicious chains preserve fund conservation within each chain",
                "suspicious activity is not only an amount threshold",
                "classifier trained on guided data transfers better to a hidden guided test set",
            ]
        },
    }


def validate_fund_conservation(frame: pd.DataFrame, tolerance: float = 2.0) -> pd.DataFrame:
    """Return per-chain conservation checks for suspicious chains."""

    suspicious = frame[(frame["label"] == "suspicious") & (frame["chain_id"] != "")]
    rows = []
    for chain_id, group in suspicious.groupby("chain_id"):
        inbound = group[group["risk_signal"] == "funding transfer before rapid split"]["amount"].sum()
        outbound = group[group["risk_signal"] != "funding transfer before rapid split"]["amount"].sum()
        rows.append(
            {
                "chain_id": chain_id,
                "inbound": round(inbound, 2),
                "outbound": round(outbound, 2),
                "difference": round(inbound - outbound, 2),
                "passes": abs(inbound - outbound) <= tolerance,
            }
        )
    return pd.DataFrame(rows)


def _score_transfer(train: pd.DataFrame, test: pd.DataFrame, seed: int) -> dict:
    train_features = _model_features(train)
    test_features = _model_features(test)
    y_train = (train["label"] == "suspicious").astype(int)
    y_true = (test["label"] == "suspicious").astype(int)

    model = Pipeline(
        steps=[
            (
                "prep",
                ColumnTransformer(
                    transformers=[
                        ("num", StandardScaler(), ["amount", "hour"]),
                        (
                            "cat",
                            OneHotEncoder(handle_unknown="ignore"),
                            [
                                "currency",
                                "channel",
                                "is_cross_border",
                                "is_typology_narrative",
                                "is_off_hours",
                            ],
                        ),
                    ]
                ),
            ),
            (
                "model",
                RandomForestClassifier(
                    n_estimators=120,
                    min_samples_leaf=4,
                    class_weight="balanced",
                    random_state=seed,
                ),
            ),
        ]
    )

    model.fit(train_features, y_train)
    y_pred = model.predict(test_features)
    return {
        "precision": round(float(precision_score(y_true, y_pred, zero_division=0)), 3),
        "recall": round(float(recall_score(y_true, y_pred, zero_division=0)), 3),
        "f1": round(float(f1_score(y_true, y_pred, zero_division=0)), 3),
        "suspicious_share": round(float(y_true.mean()), 3),
    }


def _model_features(frame: pd.DataFrame) -> pd.DataFrame:
    features = frame.copy()
    features["hour"] = features["timestamp"].dt.hour
    features["is_cross_border"] = features["origin_region"] != features["destination_region"]
    legit_terms = {
        "monthly supplier payment",
        "payroll batch",
        "platform settlement",
        "shipping invoice",
        "software subscription",
        "tax remittance",
    }
    features["is_typology_narrative"] = ~features["narrative"].isin(legit_terms)
    features["is_off_hours"] = (features["hour"] < 8) | (features["hour"] > 18)
    return features
