# DeepSeek V4 Pro Real Case Run

Provider: DeepSeek

Model: `deepseek-v4-pro`

Input: `examples/typologies/solar_case_records.txt`

API key handling: supplied at runtime; not written to disk or committed.

## Extracted Typology

- Name: Solar Export Shell Funding and Split
- Industry: Solar Energy
- Origin regions: United Kingdom, United States
- Destination regions: Hong Kong, Singapore, United Arab Emirates
- Amount range: $4,000 to $45,000
- Split count: 5 to 6
- Time window: 48 hours
- Methods: shell company funding, structured splitting, rapid outbound transfers, thin company profiles, vague trade narratives
- Narrative terms: consulting invoice, equipment deposit, logistics fee, solar panel shipment, import services

## Generated Records

- Guided CSV records: 300
- Suspicious rows: 57
- Suspicious chains: 9
- Fund conservation checks: 9/9 passed
- Minimum generated amount: $92.45
- Maximum generated amount: $40,885.26

The minimum amount is below the typology range because legitimate background traffic is intentionally noisy. Suspicious chain funding and split activity remains governed by the detected typology.

## Evaluation

The evaluation routine generates a 500-record guided training set and a 500-record rule-baseline training set, then scores both against a hidden guided test set.

| Training data | Precision | Recall | F1 |
| --- | ---: | ---: | ---: |
| Guided SynthAML data | 1.000 | 1.000 | 1.000 |
| Rule baseline data | 1.000 | 0.077 | 0.143 |

## What This Real Run Showed

DeepSeek successfully detected the laundering pattern from the case-record batch rather than from a manually written rule: solar export accounts receive shell-supplier funding, rapidly split funds to Hong Kong, Singapore, and the United Arab Emirates, and use vague trade-service narratives.

The output supports the project claim: the GenAI step can convert messy suspicious-record evidence into a structured, reviewable typology, and the guided chain-style examples are more useful for this workflow than a simple large-transfer baseline.
