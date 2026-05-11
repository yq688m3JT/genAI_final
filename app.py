"""Streamlit app for SynthAML."""

from __future__ import annotations

import json

import pandas as pd
import plotly.express as px
import streamlit as st

from synthaml import extract_typology, generate_guided_transactions, generate_rule_baseline
from synthaml.evaluate import evaluate_generators, validate_fund_conservation


st.set_page_config(page_title="SynthAML", page_icon="S", layout="wide")

st.markdown(
    """
    <style>
    :root {
      --ink: #12213a;
      --muted: #667085;
      --paper: #f7f3ea;
      --panel: #ffffff;
      --line: #ded7c8;
      --green: #0e7c66;
      --red: #c44536;
      --gold: #d89c27;
    }
    .stApp {
      background: linear-gradient(180deg, #f7f3ea 0%, #f3eee3 100%);
      color: var(--ink);
    }
    section[data-testid="stSidebar"] {
      background: #111d32;
      border-right: 1px solid rgba(255,255,255,.08);
    }
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] span {
      color: #eef2f6 !important;
    }
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3 {
      color: #ffffff !important;
    }
    .block-container {
      padding-top: 2rem;
      max-width: 1320px;
    }
    .product-bar {
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 24px;
      border-bottom: 1px solid var(--line);
      padding-bottom: 18px;
      margin-bottom: 22px;
    }
    .brand-lockup {
      display: flex;
      align-items: center;
      gap: 14px;
    }
    .brand-mark {
      width: 44px;
      height: 44px;
      display: grid;
      place-items: center;
      background: var(--ink);
      color: white;
      font-weight: 800;
      letter-spacing: .04em;
    }
    .brand-title {
      font-size: 30px;
      line-height: 1;
      font-weight: 800;
      color: var(--ink);
      margin: 0;
    }
    .brand-subtitle {
      margin-top: 4px;
      color: var(--muted);
      font-size: 14px;
    }
    .status-pill {
      border: 1px solid var(--line);
      background: rgba(255,255,255,.62);
      padding: 8px 12px;
      font-size: 13px;
      color: var(--ink);
      white-space: nowrap;
    }
    .section-label {
      color: var(--green);
      font-size: 12px;
      font-weight: 800;
      letter-spacing: .08em;
      text-transform: uppercase;
      margin-bottom: 6px;
    }
    .panel {
      background: rgba(255,255,255,.72);
      border: 1px solid var(--line);
      padding: 20px;
      min-height: 100%;
    }
    .scenario-title {
      font-size: 23px;
      font-weight: 800;
      color: var(--ink);
      margin-bottom: 8px;
    }
    .scenario-copy {
      color: #3d405b;
      font-size: 15px;
      line-height: 1.45;
    }
    .metric-row {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 12px;
      margin: 16px 0 18px;
    }
    .metric-tile {
      background: #fff;
      border: 1px solid var(--line);
      padding: 14px 16px;
    }
    .metric-value {
      font-size: 26px;
      line-height: 1;
      font-weight: 850;
      color: var(--ink);
      white-space: nowrap;
    }
    .metric-label {
      margin-top: 7px;
      font-size: 12px;
      color: var(--muted);
      text-transform: uppercase;
      letter-spacing: .05em;
      font-weight: 700;
      white-space: nowrap;
    }
    .gate-list {
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 12px;
      margin-top: 12px;
    }
    .gate {
      border-left: 4px solid var(--green);
      background: rgba(14,124,102,.08);
      padding: 12px 14px;
      color: #24443d;
      font-size: 14px;
      min-height: 64px;
    }
    div[data-testid="stMetric"] {
      background: #fff;
      border: 1px solid var(--line);
      padding: 12px 14px;
    }
    div[data-testid="stTabs"] button p {
      font-weight: 700;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


default_text = """Regulatory warning: shell companies are being used to move funds through
solar panel import/export invoices. Payments often originate in the United States or
United Kingdom, then split quickly to counterparties in Hong Kong, Singapore, and the
United Arab Emirates. Narratives mention equipment deposits, logistics fees, or solar
panel shipments. Transactions may cluster near Friday afternoon cutoff windows and
range from $4,000 to $45,000."""

with st.sidebar:
    st.markdown("## SynthAML")
    st.caption("Scenario factory controls")
    records = st.slider("Records", 50, 1000, 250, step=50)
    suspicious_ratio = st.slider("Suspicious share", 0.05, 0.35, 0.18, step=0.01)
    seed = st.number_input("Random seed", min_value=1, value=42)
    use_llm = st.toggle("Use LLM extraction when API key is available", value=False)
    provider = st.selectbox("LLM provider", ["deepseek", "openai"])
    default_model = "deepseek-v4-pro" if provider == "deepseek" else "gpt-4o-mini"
    model = st.text_input("Model", value=default_model)
    st.divider()
    st.caption("Reviewer mode")
    st.selectbox("Review queue", ["New typology intake", "Model QA package", "Export review"])
    st.selectbox("Risk appetite", ["Balanced", "High recall", "High precision"])

st.markdown(
    """
    <div class="product-bar">
      <div class="brand-lockup">
        <div class="brand-mark">SA</div>
        <div>
          <div class="brand-title">SynthAML</div>
          <div class="brand-subtitle">Typology-to-test-data workbench for financial crime model teams</div>
        </div>
      </div>
      <div class="status-pill">Defensive synthetic data only | Human review required</div>
    </div>
    """,
    unsafe_allow_html=True,
)

intake_col, scenario_col = st.columns([1.08, 0.92], gap="large")

with intake_col:
    st.markdown('<div class="section-label">Typology Intake</div>', unsafe_allow_html=True)
    typology_text = st.text_area(
        "Warning report excerpt",
        default_text,
        height=230,
        label_visibility="collapsed",
    )

config = extract_typology(typology_text, use_llm=use_llm, model=model, provider=provider)
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
metrics = evaluate_generators(config, n_records=max(records, 200), seed=int(seed))
checks = validate_fund_conservation(data)
suspicious_rows = int((data["label"] == "suspicious").sum())
suspicious_chains = int(data.loc[data["chain_id"].astype(bool), "chain_id"].nunique())
passing_checks = int(checks["passes"].sum()) if not checks.empty else 0

with scenario_col:
    st.markdown('<div class="section-label">Scenario Brief</div>', unsafe_allow_html=True)
    st.markdown(
        f"""
        <div class="panel">
          <div class="scenario-title">{config.name}</div>
          <div class="scenario-copy">{config.risk_summary}</div>
          <div class="metric-row">
            <div class="metric-tile"><div class="metric-value">{len(data):,}</div><div class="metric-label">Records</div></div>
            <div class="metric-tile"><div class="metric-value">{suspicious_chains}</div><div class="metric-label">Chains</div></div>
            <div class="metric-tile"><div class="metric-value">{suspicious_rows}</div><div class="metric-label">Signal rows</div></div>
            <div class="metric-tile"><div class="metric-value">{passing_checks}/{len(checks)}</div><div class="metric-label">Checks passed</div></div>
          </div>
          <div class="gate-list">
            <div class="gate">Structured typology constraints extracted from prose.</div>
            <div class="gate">Suspicious chains preserve funding and split logic.</div>
            <div class="gate">CSV and evaluation package ready for model QA.</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.divider()

action_col_1, action_col_2, action_col_3, action_col_4 = st.columns(4)
with action_col_1:
    st.metric("Guided F1", f'{metrics["guided"]["f1"]:.3f}')
with action_col_2:
    st.metric("Baseline F1", f'{metrics["baseline"]["f1"]:.3f}')
with action_col_3:
    st.metric("Recall uplift", f'{metrics["guided"]["recall"] - metrics["baseline"]["recall"]:.3f}')
with action_col_4:
    st.metric("Amount range", f"${config.amount_min:,.0f}-${config.amount_max:,.0f}")

tab_overview, tab_data, tab_eval, tab_export = st.tabs(
    ["Command Center", "Synthetic Ledger", "Evaluation", "Export Package"]
)

with tab_overview:
    st.markdown('<div class="section-label">Extracted Typology</div>', unsafe_allow_html=True)
    config_col, chart_col = st.columns([0.84, 1.16], gap="large")
    with config_col:
        st.json(config.to_dict(), expanded=False)
    with chart_col:
        amount_chart = px.histogram(
            data,
            x="amount",
            color="label",
            nbins=34,
            color_discrete_map={"legitimate": "#14213D", "suspicious": "#0E7C66"},
            title="Generated amount distribution",
        )
        amount_chart.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="#14213D",
            legend_title_text="",
            margin=dict(l=12, r=12, t=42, b=12),
        )
        st.plotly_chart(amount_chart, use_container_width=True)

with tab_data:
    st.markdown('<div class="section-label">Synthetic Ledger</div>', unsafe_allow_html=True)
    st.dataframe(data, use_container_width=True, height=390)
    timing_chart = px.scatter(
        data,
        x="timestamp",
        y="amount",
        color="label",
        hover_data=["narrative", "risk_signal", "chain_id"],
        color_discrete_map={"legitimate": "#14213D", "suspicious": "#0E7C66"},
        title="Transaction timing and amount by label",
    )
    timing_chart.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="#14213D",
        legend_title_text="",
        margin=dict(l=12, r=12, t=42, b=12),
    )
    st.plotly_chart(timing_chart, use_container_width=True)

with tab_eval:
    st.markdown('<div class="section-label">Model Transfer Evaluation</div>', unsafe_allow_html=True)
    score_frame = pd.DataFrame(
        [metrics["guided"], metrics["baseline"]],
        index=["Guided SynthAML data", "Rule baseline data"],
    )
    st.dataframe(score_frame, use_container_width=True)
    eval_col_1, eval_col_2 = st.columns([1, 1], gap="large")
    with eval_col_1:
        score_chart = px.bar(
            score_frame.reset_index(names="training_data"),
            x="training_data",
            y=["precision", "recall", "f1"],
            barmode="group",
            title="Classifier transfer to hidden guided typology set",
            color_discrete_sequence=["#14213D", "#0E7C66", "#C44536"],
        )
        score_chart.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="#14213D",
            legend_title_text="",
            margin=dict(l=12, r=12, t=42, b=12),
        )
        st.plotly_chart(score_chart, use_container_width=True)
    with eval_col_2:
        st.write("Fund conservation checks")
        st.dataframe(checks, use_container_width=True, height=318)

with tab_export:
    st.markdown('<div class="section-label">Export Package</div>', unsafe_allow_html=True)
    export_col_1, export_col_2, export_col_3 = st.columns(3)
    with export_col_1:
        st.download_button(
            "Download guided CSV",
            data.to_csv(index=False),
            file_name="synthaml_guided_transactions.csv",
            mime="text/csv",
            use_container_width=True,
        )
    with export_col_2:
        st.download_button(
            "Download baseline CSV",
            baseline.to_csv(index=False),
            file_name="synthaml_rule_baseline.csv",
            mime="text/csv",
            use_container_width=True,
        )
    with export_col_3:
        st.download_button(
            "Download evaluation JSON",
            json.dumps(metrics, indent=2),
            file_name="synthaml_evaluation.json",
            mime="application/json",
            use_container_width=True,
        )
    st.write("Baseline preview")
    st.dataframe(baseline, use_container_width=True, height=330)
