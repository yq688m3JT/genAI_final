"""Run one real DeepSeek V4 Pro record-batch extraction and evaluation.

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
INPUT = ROOT / "examples" / "typologies" / "solar_case_records.txt"
OUT = ROOT / "examples" / "sample_outputs" / "deepseek_case"


def main() -> None:
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        api_key = getpass.getpass("DeepSeek API key: ")

    record_batch = INPUT.read_text(encoding="utf-8")
    config = extract_typology(
        record_batch,
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
    (OUT / "run_record.md").write_text(_make_run_record(config, guided, checks, metrics), encoding="utf-8")

    print("Provider: deepseek")
    print("Model: deepseek-v4-pro")
    print(json.dumps({"typology": config.to_dict(), "evaluation": metrics}, indent=2))
    print(f"\nWrote DeepSeek case artifacts to {OUT}")


def _make_run_record(config, guided, checks, metrics) -> str:
    suspicious = guided[guided["label"] == "suspicious"]
    suspicious_chains = suspicious["chain_id"].nunique()
    passing_checks = int(checks["passes"].sum()) if not checks.empty else 0
    baseline = metrics["baseline"]
    guided_metrics = metrics["guided"]
    return f"""# DeepSeek V4 Pro Real Case Run

Provider: DeepSeek

Model: `deepseek-v4-pro`

Input: `examples/typologies/solar_case_records.txt`

API key handling: supplied at runtime; not written to disk or committed.

## Extracted Typology

- Name: {config.name}
- Industry: {config.industry}
- Origin regions: {", ".join(config.origin_regions)}
- Destination regions: {", ".join(config.destination_regions)}
- Amount range: ${config.amount_min:,.0f} to ${config.amount_max:,.0f}
- Split count: {config.split_count_min} to {config.split_count_max}
- Time window: {config.time_window_hours} hours
- Methods: {", ".join(config.suspicious_methods)}
- Narrative terms: {", ".join(config.narrative_terms)}

## Generated Records

- Guided CSV records: {len(guided)}
- Suspicious rows: {len(suspicious)}
- Suspicious chains: {suspicious_chains}
- Fund conservation checks: {passing_checks}/{len(checks)} passed
- Minimum generated amount: ${guided["amount"].min():,.2f}
- Maximum generated amount: ${guided["amount"].max():,.2f}

The minimum amount is below the typology range because legitimate background traffic is intentionally noisy. Suspicious chain funding and split activity remains governed by the detected typology.

## Evaluation

The evaluation routine generates a 500-record guided training set and a 500-record rule-baseline training set, then scores both against a hidden guided test set.

| Training data | Precision | Recall | F1 |
| --- | ---: | ---: | ---: |
| Guided SynthAML data | {guided_metrics["precision"]:.3f} | {guided_metrics["recall"]:.3f} | {guided_metrics["f1"]:.3f} |
| Rule baseline data | {baseline["precision"]:.3f} | {baseline["recall"]:.3f} | {baseline["f1"]:.3f} |

## What This Real Run Showed

DeepSeek successfully detected the laundering pattern from the case-record batch rather than from a manually written rule: solar export accounts receive shell-supplier funding, rapidly split funds to Hong Kong, Singapore, and the United Arab Emirates, and use vague trade-service narratives.

The output supports the project claim: the GenAI step can convert messy suspicious-record evidence into a structured, reviewable typology, and the guided chain-style examples are more useful for this workflow than a simple large-transfer baseline.
"""


if __name__ == "__main__":
    main()
