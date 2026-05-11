# DeepSeek V4 Pro Real Case Run

Provider: DeepSeek

Model: `deepseek-v4-pro`

Input: `examples/typologies/solar_trade_warning.txt`

API key handling: supplied at runtime; not written to disk or committed.

## Extracted Typology

- Name: Solar Equipment Exports Typology: Shell-Company Counterparties
- Industry: solar equipment exports
- Origin regions: United States, United Kingdom
- Destination regions: Hong Kong, Singapore, United Arab Emirates
- Amount range: $4,000 to $45,000
- Split count: 3 to 7
- Time window: 48 hours
- Methods: shell-company counterparties, structured splitting, false or vague invoice narratives, Friday cutoff clustering

## Generated Records

- Guided records: 300
- Suspicious rows: 58
- Suspicious chains: 8
- Fund conservation checks: 8/8 passed
- Minimum generated amount: $92.45
- Maximum generated amount: $44,058.87

The minimum amount is below the typology range because legitimate background traffic is intentionally noisy. Suspicious chain funding and split activity remains governed by the typology range.

## Evaluation

| Training data | Precision | Recall | F1 |
| --- | ---: | ---: | ---: |
| Guided SynthAML data | 1.000 | 1.000 | 1.000 |
| Rule baseline data | 1.000 | 0.064 | 0.120 |

## What This Real Run Showed

The first DeepSeek run correctly identified the AML methods, narratives, amount range, and timing window, but it misassigned origin and destination regions. That is a realistic LLM failure mode for document extraction.

I added a deterministic post-extraction guardrail for explicit region role phrases such as "payments originate in" and "to counterparties in." The final run preserved the region roles correctly while retaining the LLM-extracted typology details.

The model-transfer result still supports the project claim: guided chain-style examples are more useful for this workflow than a simple large-transfer baseline.
