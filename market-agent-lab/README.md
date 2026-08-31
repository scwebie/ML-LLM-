# Market Agent Lab v0.1

> **PAPER-TRADING / SIMULATION ONLY.** This repository has no live brokerage, betting, gambling, or
> prediction-market integration. It must not be used to execute real-money trades.

A vertically integrated quantitative research lab: deterministic synthetic OHLCV/fundamental/macro/news
data, technical features, structured research agents, LightGBM alpha models, chronological validation,
portfolio construction, immutable deterministic risk decisions, internal paper fills, DuckDB records,
controlled champion/challenger learning, FastAPI, and Streamlit monitoring.

## Architecture and safety

Research agents produce validated Pydantic output only. Outputs become versioned features; models predict
returns/probabilities—not BUY/SELL. Deterministic allocation proposes sizes, then the risk engine is the
non-bypassable gate to the internal simulated broker. Agents cannot import or invoke execution. Risk limits
and the kill switch cannot be modified autonomously. See [architecture](docs/architecture.md) and
[model design](docs/model_design.md).

## Install and run

Python 3.12+ and `uv` are required.

```bash
uv sync
uv run python main.py demo
uv run pytest
uv run ruff check .
uv run mypy . --ignore-missing-imports
uv run uvicorn api.main:app --reload
uv run streamlit run dashboard/app.py
```

Copy `.env.example` to `.env`. `OPENAI_API_KEY` is optional and is never needed by the reproducible offline
demo. `MAL_DATA_DIR`, `MAL_RANDOM_SEED`, and `MAL_KILL_SWITCH` document intended runtime configuration.
Generated Parquet, feature snapshots, DuckDB state, and `demo_summary.json` live in ignored `data_store/`.

## Demo stages

`uv run python main.py demo` generates explicitly synthetic data with seed 42, calculates deterministic
features, persists Parquet, creates forward excess-return labels, chooses a leak-free expanding fold,
trains four LightGBM estimators, predicts, allocates, risk-checks, paper-fills, backtests with costs, saves
results, and prints a concise JSON report. The API `/safety` endpoint exposes the operating boundary.

## Leakage and validation

Reporting dates are not availability dates. Point-in-time joins use publication timestamps and backward
as-of semantics; tests reject future joins. Features are calculated before forward labels; incomplete
horizons are excluded. The primary evaluation is expanding-window walk-forward validation, never a random
split: every training timestamp precedes every validation timestamp and later folds only expand history.

## Controlled retraining

Predictions are immutable. After 20 sessions, outcomes can be labelled and appended. Drift triggers a
challenger, not online model mutation. A promotion gate considers out-of-sample Sharpe, drawdown,
information ratio, error, calibration, turnover, and costs and records its reasons.

## Limitations / next milestone

Synthetic relationships and daily fills are intentionally simplified; sector concentration is represented
in configuration but needs security-master data before enforcement. The demo uses deterministic agent
fallbacks so it runs without paid APIs; production research can instantiate OpenAI Agents SDK agents with
the same schemas. Calibration charts, durable promotion history, multi-asset backtesting, limit-order queue
models, benchmark variants, and statistical confidence intervals should be deepened next. The recommended
next milestone is a strict point-in-time dataset catalogue plus multi-symbol portfolio walk-forward engine
and persisted model registry, while preserving the paper-only boundary.
