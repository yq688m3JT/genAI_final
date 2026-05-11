"""Run one real DeepSeek V4 Pro typology extraction and evaluation.

The API key is read from the environment or securely from stdin. The key is not
written to disk. Outputs are saved under examples/sample_outputs/deepseek_case.
"""

from __future__ import annotations

import getpass
import json
import os
from pathlib import Path

from synthaml import extract_typology, generate_guided_transactions, generate_rule_baseline
from synthaml.evaluate import evaluate_generators, validate_fund_conservation


ROOT = Path(__file__).parent
INPUT = ROOT / "examples" / "typologies" / "solar_trade_warning.txt"
OUT = ROOT / "examples" / "sample_outputs" / "deepseek_case"


def main() -> None:
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        api_key = getpass.getpass("DeepSeek API key: ")

    warning = INPUT.read_text(encoding="utf-8")
    config = extract_typology(
        warning,
        use_llm=True,
        provider="deepseek",
        model="deepseek-v4-pro",
        api_key=api_key,
    )
    guided = generate_guided_transactions(config, n_records=300, seed=23)
    baseline = generate_rule_baseline(config, n_records=300, seed=23)
    checks = validate_fund_conservation(guided)
    metrics = evaluate_generators(config, n_records=500, seed=23)

    OUT.mkdir(parents=True, exist_ok=True)
    guided.to_csv(OUT / "guided_transactions.csv", index=False)
    baseline.to_csv(OUT / "rule_baseline_transactions.csv", index=False)
    checks.to_csv(OUT / "fund_conservation_checks.csv", index=False)
    (OUT / "typology_config.json").write_text(json.dumps(config.to_dict(), indent=2), encoding="utf-8")
    (OUT / "evaluation_summary.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")

    print("Provider: deepseek")
    print("Model: deepseek-v4-pro")
    print(json.dumps({"typology": config.to_dict(), "evaluation": metrics}, indent=2))
    print(f"\nWrote DeepSeek case artifacts to {OUT}")


if __name__ == "__main__":
    main()
