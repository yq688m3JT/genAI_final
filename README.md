# SynthAML

SynthAML is a commercial-style GenAI workbench for AML compliance data teams. It converts a short regulatory typology warning into synthetic cross-border transaction records that can be used to test whether existing financial-crime models recognize a new pattern.

The app is intentionally narrow: it focuses on one workflow, defensive synthetic data generation for a newly reported AML typology. It does not produce advice for evading controls.

## Context, User, and Problem

The target user is an AML algorithm engineer or compliance data scientist at a cross-border payments company or bank.

When a regulator publishes a warning about a new laundering pattern, the team often has no labeled historical transactions for that pattern. That creates a cold-start problem: existing models can be tuned on known fraud, but they may miss the new typology until real losses or regulatory findings appear.

SynthAML helps the user move from a plain-language warning to a small labeled synthetic dataset that can be inspected, exported, and used for model testing.

## Solution and Design

SynthAML includes:

- A polished Streamlit workbench in `app.py`
- A reusable typology extractor in `synthaml/typology.py`
- A guided synthetic transaction generator in `synthaml/generator.py`
- A baseline generator and evaluation workflow in `synthaml/evaluate.py`
- A reproducible evaluation script in `run_evaluation.py`

The application workflow is:

1. Paste a typology warning into the app.
2. Extract structured constraints: industry, regions, narratives, suspicious methods, amount range, split count, and time window.
3. Review the commercial-style scenario brief, quality gates, and run settings.
4. Generate labeled synthetic transactions with legitimate background traffic and suspicious multi-step chains.
5. Validate that suspicious chains preserve basic fund-flow consistency.
6. Compare the guided generator against a simple amount-threshold baseline and export the QA package.

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

Optional LLM extraction with DeepSeek V4 Pro:

```bash
export DEEPSEEK_API_KEY="your_key_here"
streamlit run app.py
```

The app sidebar defaults to `deepseek` and `deepseek-v4-pro`. OpenAI-compatible extraction is also supported:

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
| Rule baseline data | 0.636 | 0.074 | 0.133 |

This is a small synthetic evaluation, not proof of production AML performance. It shows that a model trained on guided chain-style data transfers better to a hidden chain-style test set than a model trained only on amount-threshold examples.

The app itself presents the artifact as a B2B compliance workbench with a scenario intake panel, extracted typology brief, quality gates, synthetic ledger, evaluation dashboard, and export package.

### DeepSeek V4 Pro Real Case

I also ran the sample typology through DeepSeek V4 Pro using the OpenAI-compatible DeepSeek API. The key was supplied at runtime and was not written to the repository.

The real run artifacts are saved under `examples/sample_outputs/deepseek_case/`.

DeepSeek extracted:

- Origins: United States, United Kingdom
- Destinations: Hong Kong, Singapore, United Arab Emirates
- Industry: solar equipment exports
- Amount range: $4,000 to $45,000
- Methods: shell-company counterparties, structured splitting, vague invoice narratives, Friday cutoff clustering

DeepSeek case evaluation:

| Training data | Precision | Recall | F1 |
| --- | ---: | ---: | ---: |
| Guided SynthAML data | 1.000 | 1.000 | 1.000 |
| Rule baseline data | 1.000 | 0.064 | 0.120 |

The first DeepSeek run misassigned origin and destination regions, which is a realistic LLM failure. I added a deterministic role-correction guardrail for explicit phrases such as "originate in" and "to counterparties in"; the final run preserves the region roles correctly.

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

Presentation materials are included in:

- `docs/synthaml-final-presentation.pptx`
- `docs/synthaml_presentation_speech_draft.md`
- `docs/lightning_presentation.md`
