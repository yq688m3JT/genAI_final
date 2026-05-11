# SynthAML Presentation Speech Draft

Total target: 3 minutes.

Use the first four slides for the project story, then use the final three UI walkthrough slides as the demo. This version does not require a live localhost app.

## Title Slide

Hi everyone. My project is SynthAML, a commercial-style GenAI workbench for AML compliance model teams.

The narrow workflow is typology intake to test-data export. The user starts with a regulatory warning, and the goal is to create inspectable synthetic transactions that help test whether current models have a blind spot.

## Slide 1: Context, User, and Problem

The target user is an AML algorithm engineer or compliance data scientist at a cross-border payments company or bank.

The workflow problem is a cold start. When a regulator publishes a warning about a new laundering typology, the company may not have any labeled historical transactions for that pattern yet. So the model team knows what kind of behavior to look for, but they do not have examples to test against.

That matters because a simple threshold rule can miss behavior that is spread across a chain of transactions.

## Slide 2: Solution and Design

SynthAML turns a short typology warning into labeled synthetic transaction data.

The user pastes a warning into the app. The system extracts structured constraints like industry, regions, amount range, suspicious methods, narratives, and timing window. Then it generates normal background traffic plus suspicious chains: a funding transfer followed by rapid split payments to cross-border counterparties.

The GenAI design choice is the translation step from unstructured compliance prose into structured generation constraints. I also included a deterministic fallback, so the app and evaluation can still run without an API key.

## Slide 3: Evaluation and Results

For evaluation, I compared SynthAML against a simpler baseline.

The baseline generates suspicious records mostly using a large-amount rule. SynthAML generates chain-style behavior with timing, narratives, counterparties, and fund-flow consistency.

I trained one classifier on SynthAML data and one on baseline data, then tested both on a hidden guided test set from the same typology. In this sample, SynthAML reached an F1 of 1.000, while the rule baseline reached 0.189. The important result is recall: SynthAML found the hidden chain-style examples, while the threshold baseline missed most of them.

This is not a production AML benchmark, but it does show why the GenAI-guided workflow is more useful than a simple rule-only generator for this narrow task.

## Slide 4: UI Walkthrough 1

This is the main command center. The reviewer pastes a regulatory warning on the left, and the app turns it into a structured scenario brief on the right.

## Slide 5: UI Walkthrough 2

This is the evaluation tab. It compares SynthAML’s guided synthetic data against the simpler rule baseline, so the project is evaluated against a real alternative.

## Slide 6: UI Walkthrough 3

This is the export package. The user can download the guided CSV, the baseline CSV, and the evaluation JSON. So the output is usable as a model QA package, while still keeping a human reviewer in the loop.

## Short Closing

So the business value is not replacing AML experts. It is helping them turn a new typology warning into inspectable test data faster, so model teams can evaluate blind spots before real labeled cases exist.
