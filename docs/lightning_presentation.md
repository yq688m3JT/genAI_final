# SynthAML Lightning Presentation

## Slide 1: Context, User, and Problem

AML data scientists at cross-border payments firms need to test models against new laundering typologies soon after a regulatory warning appears.

The problem is a cold start: there may be no historical labeled transactions for the new pattern, so existing models can miss it.

## Slide 2: Solution and Design

SynthAML is a Streamlit app that turns a typology warning into labeled synthetic transaction data.

Design choices:

- Extract structured constraints from warning text.
- Generate legitimate background transactions plus suspicious multi-step chains.
- Preserve basic fund-flow consistency.
- Include a deterministic fallback so the project is reproducible without an API key.

## Slide 3: Evaluation and Results

Baseline: simple amount-threshold synthetic data.

Evaluation:

- Train one classifier on SynthAML guided data.
- Train another classifier on baseline data.
- Test both on a hidden guided dataset from the same typology.
- Check precision, recall, F1, and fund conservation.

Result from the included sample:

| Training data | Precision | Recall | F1 |
| --- | ---: | ---: | ---: |
| Guided SynthAML data | 1.000 | 1.000 | 1.000 |
| Rule baseline data | 0.643 | 0.098 | 0.170 |

Takeaway: threshold examples do not transfer well to chain-style typology behavior.

## Slide 4: Artifact Snapshot

Show one of these:

- The Streamlit app with generated transaction rows and amount/timing charts.
- `examples/sample_outputs/guided_transactions.csv`
- `examples/sample_outputs/evaluation_summary.json`

Talk track:

"The app lets the user paste a warning, inspect the extracted typology, generate records, run conservation checks, compare against the baseline, and export CSVs. A human compliance reviewer should still approve the scenario before using the data for model work."

## 2-3 Minute Script

SynthAML is built for AML algorithm engineers at cross-border payments companies. Their workflow problem is that regulators can publish a new laundering typology before the company has any labeled examples in its transaction history. That creates a cold-start gap for model testing.

The app takes a short warning report and extracts structured constraints such as regions, industry, narratives, amount ranges, timing, and suspicious methods. It then generates synthetic transactions with normal background traffic and suspicious chains where funds arrive, split quickly, and move cross-border with vague business narratives.

I compared it with a simple baseline that labels suspicious transactions mainly by large amount. For evaluation, I trained one classifier on SynthAML data and one on baseline data, then tested both on a hidden guided dataset. The guided data had much stronger recall on the hidden typology-style examples, while the threshold baseline missed most of them.

The main limitation is that this is still simplified synthetic data. It is useful for early testing and scenario discussion, but a compliance expert should review the extracted constraints and records before the output is used in real model development.
