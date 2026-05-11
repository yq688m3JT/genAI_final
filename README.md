# SynthAML

SynthAML is a small GenAI workflow for AML compliance data teams. It converts a short regulatory typology warning into synthetic cross-border transaction records that can be used to test whether existing financial-crime models recognize a new pattern.

The app is intentionally narrow: it focuses on one workflow, defensive synthetic data generation for a newly reported AML typology. It does not produce advice for evading controls.

## Context, User, and Problem

The target user is an AML algorithm engineer or compliance data scientist at a cross-border payments company or bank.

When a regulator publishes a warning about a new laundering pattern, the team often has no labeled historical transactions for that pattern. That creates a cold-start problem: existing models can be tuned on known fraud, but they may miss the new typology until real losses or regulatory findings appear.

SynthAML helps the user move from a plain-language warning to a small labeled synthetic dataset that can be inspected, exported, and used for model testing.

## Solution and Design

SynthAML includes:

- A Streamlit app in `app.py`
- A reusable typology extractor in `synthaml/typology.py`
- A guided synthetic transaction generator in `synthaml/generator.py`
- A baseline generator and evaluation workflow in `synthaml/evaluate.py`
- A reproducible evaluation script in `run_evaluation.py`

The workflow is:

1. Paste a typology warning into the app.
2. Extract structured constraints: industry, regions, narratives, suspicious methods, amount range, split count, and time window.
3. Generate labeled synthetic transactions with legitimate background traffic and suspicious multi-step chains.
4. Validate that suspicious chains preserve basic fund-flow consistency.
5. Compare the guided generator against a simple amount-threshold baseline.

The GenAI design choice is the typology extraction step. If `OPENAI_API_KEY` is set, SynthAML can use an OpenAI model to convert warning text into structured generation constraints. If no key is available, it falls back to a deterministic heuristic extractor so the grader can still run the app and evaluation.

## Why GenAI Is Useful

The business input is unstructured: a regulator or compliance team describes behavior in prose, not in a schema. A GenAI extractor can translate that prose into a structured scenario: relevant industries, counterparties, transaction narratives, timing patterns, and behavioral signals.

A simpler rule-only tool can generate obvious anomalies, such as large transactions above a threshold. That is useful as a baseline, but it does not capture the business logic of a laundering chain: funding, rapid splitting, cross-border movement, and vague invoice narratives.

## Setup

Create a virtual environment and install dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Optional LLM extraction:

```bash
export OPENAI_API_KEY="your_key_here"
```

Do not commit `.env`, API keys, customer data, or private reports.

## Usage

Run the app:

```bash
streamlit run app.py
```

Run the reproducible evaluation:

```bash
python run_evaluation.py
```

Run tests:

```bash
python -m pytest -q
```

## Example Input

The repository includes a sample warning at `examples/typologies/solar_trade_warning.txt`.

It describes shell companies using solar panel import/export invoices, rapid splitting, vague logistics narratives, and cross-border transfers to Hong Kong, Singapore, and the United Arab Emirates.

## Artifact Snapshot

Running `python run_evaluation.py` writes these artifacts:

- `examples/sample_outputs/guided_transactions.csv`
- `examples/sample_outputs/rule_baseline_transactions.csv`
- `examples/sample_outputs/fund_conservation_checks.csv`
- `examples/sample_outputs/typology_config.json`
- `examples/sample_outputs/evaluation_summary.json`

Sample evaluation from the included typology:

| Training data | Precision | Recall | F1 |
| --- | ---: | ---: | ---: |
| Guided SynthAML data | 1.000 | 1.000 | 1.000 |
| Rule baseline data | 0.643 | 0.098 | 0.170 |

This is a small synthetic evaluation, not proof of production AML performance. It shows that a model trained on guided chain-style data transfers better to a hidden chain-style test set than a model trained only on amount-threshold examples.

## Evaluation and Results

Baseline: a simple rule generator that labels suspicious records primarily by large transaction amount.

Guided system: a typology-aware generator that creates suspicious transaction chains with funding transfers, split outgoing payments, cross-border destinations, relevant narratives, and timing windows.

Test setup:

- Generate training data from SynthAML and from the rule baseline.
- Generate a hidden guided test set from the same typology with a different random seed.
- Train a small random forest classifier on each training set.
- Score both models on the hidden test set using precision, recall, and F1.
- Check fund conservation for suspicious chains.

What counted as good output:

- Suspicious chains preserve fund conservation within a small rounding tolerance.
- Suspicious records are not merely large transactions.
- The guided generator improves recall on hidden chain-style examples compared with the rule baseline.
- Outputs remain inspectable by a human compliance reviewer.

What worked:

- The guided generator created coherent suspicious chains and legitimate background traffic.
- The baseline comparison showed why threshold-only synthetic examples are brittle.
- The app exposes the extracted typology, generated records, charts, conservation checks, and downloadable CSVs.

What failed or remains limited:

- The generated data is still synthetic and simplified. It should not be used as production training data without expert review.
- The fallback extractor is keyword-based and less flexible than the LLM path.
- The current model evaluation is small and illustrative; a real team would test against richer historical typologies and analyst-labeled cases.
- Human compliance experts should review extracted constraints and sample records before using exports in model development.

## Repository Structure

```text
.
├── app.py
├── run_evaluation.py
├── synthaml/
│   ├── typology.py
│   ├── generator.py
│   └── evaluate.py
├── examples/
│   ├── typologies/
│   └── sample_outputs/
├── tests/
├── docs/
└── requirements.txt
```

## Lightning Presentation

Presentation notes are included in `docs/lightning_presentation.md`.
