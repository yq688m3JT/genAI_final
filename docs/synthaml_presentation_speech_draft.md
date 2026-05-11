# SynthAML Presentation Speech Draft

Target length: about 3 minutes total: roughly 2 minutes of slides, then 1 minute live browser demo.

## Slide 1: Title

Hi everyone. My project is SynthAML, a GenAI workbench for AML model QA teams.

The narrow business workflow is typology intake to model QA export. A regulatory warning or internal typology note enters the compliance workflow, and SynthAML helps turn that source into reviewed synthetic transaction data for testing model blind spots.

## Slide 2: Context, User, and Problem

The target user is an AML algorithm engineer or compliance data scientist at a bank or cross-border payments company.

The core problem is a data cold start. When a regulator publishes a new typology, the team may understand the risk, but it often has no labeled historical examples yet. That makes it hard to test whether current monitoring logic would catch the pattern.

This matters because many typologies are not just one large suspicious transaction. They are behaviors across a chain: a funding transfer, rapid splits, cross-border counterparties, vague invoices, and timing patterns. A simple threshold rule can miss that structure.

## Slide 3: Application Workflow

SynthAML is designed around that workflow, not as a general chatbot.

In a real workflow, the source would come from a regulatory watch feed, an uploaded memo, a case queue, or an internal knowledge base. The demo preloads one source packet so I can show the workflow quickly.

The system extracts a structured typology: regions, amount range, timing window, split count, narratives, and suspicious methods. A human reviewer then approves or edits those constraints. After approval, the app generates normal background traffic plus suspicious transaction chains, evaluates the guided data against a baseline, and exports a QA package.

The GenAI design choice is focused: use the model to translate unstructured compliance prose into structured, reviewable generation constraints. The deterministic fallback keeps the project runnable without an API key.

## Slide 4: Evaluation and Results

I included a baseline because in real AML QA, a new GenAI workflow has to beat the cheap alternative.

The baseline is a simpler threshold-style generator. SynthAML generates chain-style behavior with timing, counterparties, narratives, and fund-flow consistency. In the included evaluation, the guided SynthAML data reached an F1 of 1.000 on a hidden guided test set, while the baseline reached 0.133. The important difference is recall: SynthAML found the chain-style examples, while the simple baseline missed most of them.

This is not a production AML benchmark, but it shows that the workflow adds value beyond making a nicer-looking dataset.

## Slide 5: Why This Workflow Matters

The real bottleneck is not just generating rows. It is converting vague typology language into testable behavior.

The status quo could be an analyst reviewing an incoming warning, writing ad hoc rules, and creating a small prompt-only or spreadsheet sample. The risk is that the data overfits obvious signals like high amount. SynthAML makes the intermediate scenario explicit, so the reviewer can inspect what the system believes the typology means before any export is used.

## Slide 6: What the App Does

The app has five practical work areas: intake, scenario review, generation plan, ledger analysis, and evaluation plus export.

That makes it look and behave like a real internal tool. The analyst can review constraints, adjust settings, filter generated transactions, compare against a baseline, and export the files a model QA team would actually need.

## Slide 7: Live Demo Plan

For the final minute, I will click the browser demo link.

I will show four things quickly: imported-source intake and extraction, editable scenario review, the ledger and evaluation comparison, and the export package. The goal is to show that the artifact exists as a usable workflow, not only as slides.

## Closing

The business value is not replacing AML experts. It is helping them move faster from a new typology warning to inspectable test data, so model teams can evaluate blind spots before real labeled cases exist.

## Ultra-Short Version

SynthAML solves a cold-start problem for AML model QA. It turns a new typology warning into reviewed synthetic transaction chains, compares the guided output against a simpler baseline, and exports a QA package. GenAI is useful because the input is unstructured compliance prose, but a human reviewer stays involved before the synthetic data is used.
