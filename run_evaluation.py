"""Run SynthAML's reproducible evaluation and save sample artifacts."""

from __future__ import annotations

import json
from pathlib import Path

from synthaml import extract_typology, generate_guided_transactions, generate_rule_baseline
from synthaml.evaluate import evaluate_generators, validate_fund_conservation


ROOT = Path(__file__).parent
INPUT = ROOT / "examples" / "typologies" / "solar_trade_warning.txt"
OUT = ROOT / "examples" / "sample_outputs"


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    config = extract_typology(INPUT.read_text(encoding="utf-8"))
    guided = generate_guided_transactions(config, n_records=300, seed=11)
    baseline = generate_rule_baseline(config, n_records=300, seed=11)
    metrics = evaluate_generators(config, n_records=500, seed=11)
    checks = validate_fund_conservation(guided)

    guided.to_csv(OUT / "guided_transactions.csv", index=False)
    baseline.to_csv(OUT / "rule_baseline_transactions.csv", index=False)
    checks.to_csv(OUT / "fund_conservation_checks.csv", index=False)
    (OUT / "typology_config.json").write_text(json.dumps(config.to_dict(), indent=2), encoding="utf-8")
    (OUT / "evaluation_summary.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")

    print(json.dumps(metrics, indent=2))
    print(f"\nWrote artifacts to {OUT}")


if __name__ == "__main__":
    main()
