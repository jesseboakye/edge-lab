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

## Phase 3 — Re-evaluated after Phase 2 Outcome (valid gate, FAIL)

### Phase 3A — Failure Diagnosis (immediate)
- Produce attribution report by regime, cost mode, turnover bucket, and rolling-window cohorts
- Create hypothesis backlog with expected impact + test design + success criteria
- Define promotion preconditions before full ML build:
  - maintain validity PASS
  - reduce collapse ratio below threshold
  - improve OOS consistency

### Phase 3B — ML Signal Development (conditional)
- Build leakage-safe feature/label pipeline (fit on train, apply to test only)
- Start with baseline probabilistic models and calibrated outputs
- Integrate EV-aware execution policy:
  - cost-aware entry threshold
  - turnover controls
  - fractional Kelly + exposure caps
- Re-run full robustness suite unchanged for apples-to-apples comparison

### Phase 3C — Final Holdout Decision
- If Phase 3B robustness passes, run one vaulted holdout in `--mode final`
- Record holdout ledger entry and make promote/reject decision

## Phase 4 — Optional Integrations (Deferred)
- Only after Phase 3C holdout gate passes
- Venue adapters (Kalshi/Polymarket/futures)
