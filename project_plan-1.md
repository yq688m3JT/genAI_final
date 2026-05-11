# Project Plan: SynthAML

## 1. Project Title

**SynthAML**: Record-Driven AML Typology Discovery and Synthetic Model QA Workbench

## 2. Target User, Workflow, and Business Value

**Target user:** AML algorithm engineers and compliance data scientists at cross-border payments companies or banks.

**Narrow workflow:** Move from suspicious laundering records to a validated candidate typology, then generate synthetic transaction chains for model QA.

**Business value:** AML teams often see scattered suspicious records before an emerging pattern is formalized as a reusable typology. SynthAML helps reduce that pattern cold-start gap by using GenAI to infer a reviewable typology from messy records, then turning the validated pattern into inspectable synthetic test data.

## 3. Problem Statement and GenAI Fit

**Problem:** Existing monitoring models are usually strongest on known patterns. When suspicious records suggest a new chain-style behavior, teams need a faster way to convert that evidence into model-test scenarios.

**Why GenAI fits:** The input is unstructured: case notes, closed SAR summaries, suspicious transaction samples, and analyst comments. A GenAI model can detect recurring structure across the records, such as industries, regions, narratives, timing windows, split behavior, and shell-company counterparty signals.

**Why a simpler tool is not enough:** A threshold rule can flag large transactions, but it misses behavior expressed across a chain: funding transfer, rapid splitting, cross-border destinations, vague invoice narratives, and fund-flow consistency.

## 4. Final System Design and Baseline

SynthAML includes:

- A static browser demo for live presentation: `docs/demo.html`
- A Streamlit workbench for local runs: `app.py`
- A typology extractor with provider-based LLM support and deterministic fallback: `synthaml/typology.py`
- A guided synthetic transaction generator: `synthaml/generator.py`
- A baseline generator and evaluation script: `run_evaluation.py`

Workflow:

1. Self-intake suspicious records or closed case notes.
2. Use GenAI to detect a candidate typology.
3. Let a human reviewer approve or reject the detected pattern.
4. Generate legitimate background records plus suspicious multi-step chains.
5. Validate fund conservation and compare against a simple amount-threshold baseline.
6. Export a model QA package.

## 5. Evaluation Plan

The evaluation compares:

- **Guided SynthAML data:** chain-style records generated from the detected typology.
- **Rule baseline data:** simpler suspicious examples driven mainly by transaction amount.

Metrics:

- Precision, recall, and F1 on a hidden guided test set.
- Fund-conservation checks for suspicious chains.
- Human inspectability of the detected typology and generated records.

Included sample result:

| Training data | Precision | Recall | F1 |
| --- | ---: | ---: | ---: |
| Guided SynthAML data | 1.000 | 1.000 | 1.000 |
| Rule baseline data | 0.636 | 0.074 | 0.133 |

This is an illustrative class project evaluation, not a production AML benchmark.

## 6. Example Inputs and Failure Cases

Example input records describe solar equipment exporters receiving funding transfers, rapidly splitting funds to Hong Kong, Singapore, and the United Arab Emirates, and using vague invoice narratives such as consulting invoice, equipment deposit, and logistics fee.

Failure cases:

- The LLM can infer the wrong origin/destination roles from messy prose.
- Synthetic data can become too clean or regular if the generator is not constrained.
- A detected typology may be plausible but still not supported strongly enough by the record evidence.

## 7. Risks and Governance

- Defensive use only: synthetic data is for model QA, not evidence of real activity.
- No real customer PII is required for the demo.
- API keys must be supplied through environment variables or server-side secrets, never committed.
- Human compliance validation stays central before any export is used for model development.
