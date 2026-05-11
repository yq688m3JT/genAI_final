# SynthAML Presentation Speech Draft

Target length: about 3 minutes total: roughly 2 minutes of slides, then 1 minute live browser demo.

## Slide 1: Title

Hi everyone. My project is SynthAML, a GenAI workbench for AML model QA teams.

The narrow business workflow is laundering-pattern discovery to model QA export. Instead of asking humans to manually define rules, the system uses GenAI to self-intake a batch of suspicious laundering records, infer a candidate typology, and turn that detected pattern into synthetic transaction data for model testing.

## Slide 2: Context, User, and Problem

The target user is an AML algorithm engineer or compliance data scientist at a bank or cross-border payments company.

The core problem is a pattern cold start. A team may have scattered suspicious records or closed case notes, but the recurring behavior is not yet formalized as a reusable typology. That makes it hard to test whether monitoring models can detect the emerging pattern.

This matters because laundering behavior is usually not one obvious transaction. It can be a chain: funding transfer, rapid splitting, shell-company counterparties, vague invoices, and cross-border movement. Humans should not have to hand-write every rule before the system can help.

## Slide 3: Application Workflow

SynthAML is designed around LLM-assisted pattern discovery.

First, records come from confirmed investigations, suspicious transaction samples, closed SAR cases, or analyst-labeled transaction notes. The LLM self-intakes this record batch and proposes a candidate laundering typology: regions, amount range, timing window, split count, narratives, and suspicious methods.

The human role is not to set rules from scratch. The human role is to validate the detected pattern: does it match the evidence, is it plausible, and is it safe to use for model QA? After approval, the app generates normal background traffic plus suspicious transaction chains, evaluates the guided data against a baseline, and exports a QA package.

## Slide 4: Evaluation and Results

I included a baseline because in real AML QA, a new GenAI workflow has to beat the cheap alternative.

The baseline is a simpler threshold-style generator. SynthAML generates chain-style behavior with timing, counterparties, narratives, and fund-flow consistency. In the included evaluation, the guided SynthAML data reached an F1 of 1.000 on a hidden guided test set, while the baseline reached 0.133. The important difference is recall: SynthAML found the chain-style examples, while the simple baseline missed most of them.

This is not a production AML benchmark, but it shows that pattern-aware generated data can add value beyond a simple threshold workflow.

## Slide 5: Why This Workflow Matters

The real bottleneck is not generating rows. It is detecting a reusable typology from messy case evidence and making it operational for model testing.

The status quo could be an analyst reviewing records, writing ad hoc rules, and creating a small prompt-only or spreadsheet sample. The risk is that the result overfits obvious signals like high amount. SynthAML makes the detected pattern explicit, so the reviewer can inspect what the LLM inferred before any synthetic data is used.

## Slide 6: What the App Does

The app has five practical work areas: record self-intake, detected pattern review, generation plan, ledger analysis, and evaluation plus export.

That makes it behave like a real internal tool. The analyst can review the LLM-discovered typology, adjust generation settings, filter generated transactions, compare against a baseline, and export the files a model QA team would actually need.

## Slide 7: Live Demo Plan

For the final minute, I will click the browser demo link.

I will show four things quickly: the synced laundering-record queue and pattern discovery, detected pattern review, the synthetic ledger plus baseline evaluation, and the export package. The goal is to show that the artifact exists as a usable workflow, not only as slides.

## Closing

The business value is not replacing AML experts. It is helping them move faster from scattered suspicious records to a validated typology and inspectable test data, so model teams can evaluate blind spots before the pattern is fully mature in production labels.

## Ultra-Short Version

SynthAML uses GenAI to infer a candidate laundering typology from suspicious record batches, then turns the validated pattern into synthetic transaction chains for AML model QA. The human reviewer validates the detected pattern; they do not manually write rules from scratch.
