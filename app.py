"""Streamlit app for SynthAML."""

from __future__ import annotations

import json

import pandas as pd
import plotly.express as px
import streamlit as st

from synthaml import extract_typology, generate_guided_transactions, generate_rule_baseline
from synthaml.evaluate import evaluate_generators, validate_fund_conservation


st.set_page_config(page_title="SynthAML", page_icon="S", layout="wide")

st.title("SynthAML")
st.caption("Defensive AML typology-to-synthetic-transaction workflow for compliance data teams")

with st.sidebar:
    st.header("Generation Settings")
    records = st.slider("Records", 50, 1000, 250, step=50)
    suspicious_ratio = st.slider("Suspicious share", 0.05, 0.35, 0.18, step=0.01)
    seed = st.number_input("Random seed", min_value=1, value=42)
    use_llm = st.toggle("Use OpenAI extraction when API key is available", value=False)
    model = st.text_input("OpenAI model", value="gpt-4o-mini")

default_text = """Regulatory warning: shell companies are being used to move funds through
solar panel import/export invoices. Payments often originate in the United States or
United Kingdom, then split quickly to counterparties in Hong Kong, Singapore, and the
United Arab Emirates. Narratives mention equipment deposits, logistics fees, or solar
panel shipments. Transactions may cluster near Friday afternoon cutoff windows and
range from $4,000 to $45,000."""

typology_text = st.text_area("Paste a typology warning or short case description", default_text, height=210)

config = extract_typology(typology_text, use_llm=use_llm, model=model)

summary_col, export_col = st.columns([2, 1])
with summary_col:
    st.subheader(config.name)
    st.write(config.risk_summary)
    st.json(config.to_dict(), expanded=False)

data = generate_guided_transactions(
    config,
    n_records=records,
    suspicious_ratio=suspicious_ratio,
    seed=int(seed),
)
baseline = generate_rule_baseline(
    config,
    n_records=records,
    suspicious_ratio=suspicious_ratio,
    seed=int(seed),
)

with export_col:
    st.metric("Generated records", len(data))
    st.metric("Suspicious chains", data["chain_id"].astype(bool).sum())
    st.download_button(
        "Download guided CSV",
        data.to_csv(index=False),
        file_name="synthaml_guided_transactions.csv",
        mime="text/csv",
    )
    st.download_button(
        "Download baseline CSV",
        baseline.to_csv(index=False),
        file_name="synthaml_rule_baseline.csv",
        mime="text/csv",
    )

tab_data, tab_eval, tab_compare = st.tabs(["Generated Data", "Evaluation", "Baseline Comparison"])

with tab_data:
    st.dataframe(data, use_container_width=True, height=420)
    chart_col_1, chart_col_2 = st.columns(2)
    with chart_col_1:
        st.plotly_chart(
            px.histogram(data, x="amount", color="label", nbins=35, title="Amount Distribution"),
            use_container_width=True,
        )
    with chart_col_2:
        st.plotly_chart(
            px.scatter(
                data,
                x="timestamp",
                y="amount",
                color="label",
                hover_data=["narrative", "risk_signal", "chain_id"],
                title="Transaction Timing",
            ),
            use_container_width=True,
        )

with tab_eval:
    metrics = evaluate_generators(config, n_records=max(records, 200), seed=int(seed))
    st.write("Isolation Forest comparison on generated labels")
    st.dataframe(pd.DataFrame([metrics["guided"], metrics["baseline"]], index=["Guided", "Rule baseline"]))
    checks = validate_fund_conservation(data)
    st.write("Fund conservation checks")
    st.dataframe(checks, use_container_width=True)
    st.download_button(
        "Download evaluation JSON",
        json.dumps(metrics, indent=2),
        file_name="synthaml_evaluation.json",
        mime="application/json",
    )

with tab_compare:
    st.write(
        "The baseline uses a simple large-transfer rule. SynthAML's guided generator creates "
        "multi-transaction chains with timing, narratives, counterparties, and conservation checks."
    )
    st.dataframe(baseline, use_container_width=True, height=360)
