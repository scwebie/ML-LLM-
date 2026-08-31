import json
from pathlib import Path

import pandas as pd
import streamlit as st

st.set_page_config(page_title="Market Agent Lab",layout="wide");st.title("Market Agent Lab — PAPER SIMULATION")
path=Path("data_store/demo_summary.json"); summary=json.loads(path.read_text()) if path.exists() else {}
tabs=st.tabs(["Portfolio","Model","Agents","Backtest","Risk"])
with tabs[0]: st.metric("Simulated equity",f"${summary.get('equity',0):,.2f}");st.metric("Cash",f"${summary.get('cash',0):,.2f}");st.json(summary.get("positions",{}))
with tabs[1]: st.write("Champion",summary.get("model_version","not trained"));st.json(summary.get("model_metrics",{}));st.bar_chart(pd.Series(summary.get("feature_importance",{})))
with tabs[2]: st.json(summary.get("agent_report",{}));st.metric("Disagreement",summary.get("agent_disagreement",0))
with tabs[3]: st.json(summary.get("backtest_metrics",{}));
with tabs[4]: st.error("Kill switch ON" if summary.get("kill_switch") else "Kill switch OFF");st.json(summary.get("risk_decisions",[]))
