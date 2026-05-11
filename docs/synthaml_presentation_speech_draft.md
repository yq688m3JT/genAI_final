# SynthAML Presentation Speech Draft

Total target: 3 minutes.

Use the slides for the first 2 minutes, then switch to the running app for a 1-minute demo.

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

## Slide 4: Demo Setup

Now I’ll show the artifact quickly.

## 1-Minute Demo Playthrough

Open the app at `http://localhost:8501`.

First, show the sample warning text in the main text area. Say:

"This is the kind of regulatory warning the user starts with."

Next, point to the extracted typology JSON. Say:

"The app turns the prose into structured constraints: regions, narratives, suspicious methods, amount range, and timing."

Then scroll to the generated data table or chart. Say:

"Here are labeled synthetic records. Some are legitimate background traffic, and some are suspicious chain transactions."

Open the Evaluation tab. Say:

"The app also compares the guided generator against the simpler rule baseline and checks fund conservation for suspicious chains."

Finally, point to the download buttons. Say:

"The output is usable: the reviewer can inspect it and export CSVs for model testing. A human compliance expert should still approve the scenario before using it in real model development."

## Short Closing

So the business value is not replacing AML experts. It is helping them turn a new typology warning into inspectable test data faster, so model teams can evaluate blind spots before real labeled cases exist.
