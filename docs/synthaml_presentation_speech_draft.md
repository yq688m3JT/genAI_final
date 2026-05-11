# SynthAML Presentation Speech Draft

Target length: about 3 minutes.

Use the clickable browser demo link in the deck for the final minute. The demo is a static commercial-style web walkthrough, so it works on a public computer without a Streamlit account or API key.

## Slide 1: Title

Hi everyone. My project is SynthAML, a commercial-style GenAI workbench for AML compliance model teams.

The narrow workflow is typology intake to test-data export. A user starts with a regulatory warning, and SynthAML helps turn that warning into inspectable synthetic transactions for model QA.

## Slide 2: Context, User, and Problem

The target user is an AML algorithm engineer or compliance data scientist at a cross-border payments company or bank.

The problem is a cold start. When a regulator publishes a new laundering typology, the company may know the pattern exists, but it may not have labeled historical transactions for that pattern yet.

That matters because a simple threshold rule can miss behavior that is spread across a chain of transactions.

## Slide 3: Solution and Design

SynthAML turns a short typology warning into labeled synthetic transaction data.

The user pastes a warning into the app. The system extracts structured constraints like industry, regions, amount range, suspicious methods, narratives, and timing window. Then it generates normal background traffic plus suspicious chains: a funding transfer followed by rapid split payments to cross-border counterparties.

The GenAI design choice is the translation step from unstructured compliance prose into structured generation constraints. I also included a deterministic fallback, so the app and evaluation can still run without an API key.

## Slide 4: Evaluation and Results

For evaluation, I compared SynthAML against a simpler baseline.

The baseline generates suspicious records mostly using a large-amount rule. SynthAML generates chain-style behavior with timing, narratives, counterparties, and fund-flow consistency.

I trained one classifier on SynthAML data and one on baseline data, then tested both on a hidden guided test set from the same typology. In this sample, SynthAML reached an F1 of 1.000, while the rule baseline reached 0.133. The important result is recall: SynthAML found the hidden chain-style examples, while the threshold baseline missed most of them.

This is not a production AML benchmark, but it shows why the GenAI-guided workflow is more useful than a simple rule-only generator for this narrow task.

## Slide 5: UI Walkthrough 1

For the demo, I will click the browser link in the deck. The first screen is the command center: the reviewer pastes a regulatory warning on the left, and the app turns it into a structured scenario brief on the right.

## Slide 6: UI Walkthrough 2

Then I click into generated data and evaluation. The demo shows sample synthetic transactions and compares SynthAML’s guided synthetic data against the simpler rule baseline, so the project is evaluated against a real alternative instead of only showing one successful example.

## Slide 7: UI Walkthrough 3

Finally I open the export package. The user can access the guided CSV, the baseline CSV, and the evaluation JSON. So the output is usable as a model QA package, while still keeping a human reviewer in the loop.

## Closing

The business value is not replacing AML experts. It is helping them turn a new typology warning into inspectable test data faster, so model teams can evaluate blind spots before real labeled cases exist.

## Ultra-Short Version

SynthAML is a GenAI workbench for AML model teams. It solves a cold-start problem: when a new laundering typology is published, teams often do not have labeled examples yet. The app extracts structured constraints from the warning, generates synthetic transaction chains, compares them against a simple baseline, and exports a model QA package. The evaluation shows the guided data transfers much better to hidden chain-style examples than a threshold baseline. A human reviewer still stays involved before any output is used.
