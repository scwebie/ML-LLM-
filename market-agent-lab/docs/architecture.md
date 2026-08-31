# Architecture

```mermaid
flowchart TD
 A[Research agents: structured research only] --> F[Versioned feature store]
 F --> M[LightGBM alpha models]
 M --> P[Deterministic portfolio allocation]
 P --> R{Deterministic risk engine}
 R -->|approved| E[Internal paper broker]
 R -->|rejected + reason| D[(DuckDB audit records)]
 E --> D
 D --> O[Outcome labelling and drift]
 O --> C[Challenger training + walk-forward evaluation]
 C --> G{Multi-metric promotion gate}
 G --> M
```

## Safety boundary

There is no live-broker adapter. Agents terminate at structured research features and have no
reference to the execution layer. Allocation, risk approval, kill switch, fills and accounting are
deterministic code. DuckDB is hidden behind a repository boundary so a later PostgreSQL adapter can
implement the same append/list contract.
