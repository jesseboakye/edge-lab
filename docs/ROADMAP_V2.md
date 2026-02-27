# Edge-Lab Roadmap v2 (Fair Value + EV-Aware Backbone)

## Phase 1 — Backbone (Current)
- Modular architecture + TDD
- Config-driven runs (YAML default)
- Backtest + walk-forward + baseline reports

## Phase 1.5 — Fair Value + EV-Aware Execution/Sizing (Inserted)
- Probability -> fair value modeling (`edge_lab.models`)
- Unified cost engine with mode switch:
  - `bps` on notional
  - `per_unit` fee (cents/share/contract style)
  - spread + asymmetric entry/exit slippage
- Backtester config-controlled cost mode selection
- Fractional Kelly sizing with max exposure caps

## Phase 2 — Robustness (Kept, formalized)
- Cost stress under both cost modes
- Regime definitions:
  - `stress`: high-vol windows / drawdown-dense periods
  - `calm`: low-vol windows
- Collapse criteria:
  - rolling Sharpe below configured floor in >= X% windows
  - or OOS total return <= 0 in >= X% windows
- Feature perturbation/noise tests
- Stability reports with explicit collapse flags

## Phase 2.5 — Vaulted Holdout + Reproducibility Metadata
- Reserve immutable holdout split (not touched in tuning)
- Store metadata in every report:
  - config hash
  - git commit
  - run timestamp
  - data split identifiers

## Phase 3 — ML Signal Layer
- Feature pipeline + target labeling
- Strict no-leakage fit/transform on train only
- Evaluate in walk-forward + holdout

## Phase 4 — Optional Integrations (Deferred)
- Only after Phase 2 and holdout gates pass
- Venue adapters (Kalshi/Polymarket/futures)
