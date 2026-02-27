# EDGE-LAB PROJECT PLAN

## 1) Project Goal
Build and evaluate a machine learning system that predicts short-term directional returns with positive risk-adjusted performance after transaction costs.

### Edge Definition (Acceptance Criteria)
An edge exists only if all of the following hold:
- Sharpe ratio > 1.0 (after costs)
- Positive net returns over out-of-sample period
- Stable performance across rolling windows
- Performance does not collapse under minor perturbations

---

## 2) Scope

### In Scope (Phase 1)
- Local Python package structure (`edge_lab`)
- Strategy interface + at least one concrete strategy
- Backtest engine for single-asset OHLCV time series
- Basic execution model (market orders, configurable fees/slippage)
- Core performance metrics (return, drawdown, Sharpe-like ratio)
- CLI entry point for running backtests from config
- Test suite for smoke + core logic
- Documentation for architecture and usage

### Out of Scope (Phase 1)
- Full live-trading execution
- Broker integrations
- Real-time distributed system
- Web dashboard (optional later)

---

## 3) Success Criteria
- Can run: `python -m edge_lab ...` or CLI equivalent with a config file
- Reproducible backtest results from fixed input data
- Metrics output validated by tests
- Clean module boundaries (strategy vs engine vs metrics)
- Minimum 80% coverage on critical modules (engine, strategies, metrics)

## 3.1) Priority Override (Engineering-First Backbone)
Phase 1 (highest priority):
- Clean modular architecture
- Reproducibility
- Config-driven runs
- Walk-forward validation + backtesting
- TDD with runnable tests in environment

Phase 2 (only after Phase 1 runs end-to-end and tests pass):
- Cost stress tests (5/10/20 bps)
- Regime-split tests (e.g., crash vs low-vol)
- Feature perturbation/noise robustness checks
- Rolling-window stability reporting (explicitly call out collapse if observed)

Defer optional integrations (Kalshi/futures adapters) until after backbone + Phase 2 robustness.

---

## 4) Architecture (Target)

### Core Modules
- `edge_lab.backtest.engine`
  - Simulation loop
  - Signal ingestion
  - Position/account state transitions
  - Order fill logic
- `edge_lab.strategies.base`
  - Strategy contract (inputs/outputs)
- `edge_lab.strategies.*`
  - Concrete strategy implementations
- `edge_lab.metrics.performance`
  - Return, volatility, drawdown, Sharpe/Sortino (as available)
- `edge_lab.data` (to add)
  - CSV/parquet loaders
  - Data validation and normalization
- `edge_lab.config` (to add)
  - Pydantic/dataclass config models

### Data Flow
1. Load & validate market data
2. Initialize strategy + portfolio state
3. Iterate bars and generate signals
4. Apply execution model and update holdings/cash
5. Track equity curve and trades
6. Compute and persist metrics/artifacts

---

## 5) Milestones

### M1.5 — Fair Value + EV-Aware Execution/Sizing (inserted)
- Add probability -> fair price modeling utilities
- Add unified cost engine with mode switch (`bps`, `per_unit`)
- Support spread and asymmetric entry/exit slippage
- Wire cost mode switching through config into backtester
- Add fractional Kelly sizing utilities + exposure caps
- Re-run cost stress under both cost modes

**Deliverable:** EV-aware backbone before ML/integrations.

### M0 — Foundation (Current Scaffold → Stable Baseline)
- Finalize package layout
- Add `pyproject.toml` and tooling config
- Add lint/format/test tooling (ruff + pytest)
- Improve smoke test coverage

**Deliverable:** Repository with reliable local dev/test workflow.

### M1 — Engine v1 (Single Asset)
- Define candle schema and event loop contract
- Implement deterministic signal→order→fill→position pipeline
- Add transaction fee/slippage parameters
- Add trade log + equity curve tracking

**Deliverable:** Backtests run on one symbol/timeframe with consistent output.

### M2 — Strategy Layer v1
- Define strict strategy API (warmup handling, signal semantics)
- Implement baseline strategies:
  - Moving Average Crossover
  - Mean Reversion (simple z-score)
- Add strategy unit tests

**Deliverable:** Multiple strategies runnable without engine changes.

### M3 — Metrics & Reporting v1
- Implement metrics:
  - Total return
  - CAGR (if date index available)
  - Max drawdown
  - Volatility
  - Sharpe (basic)
- Add result serialization (JSON + CSV)

**Deliverable:** Standardized backtest summary and machine-readable outputs.

### M4 — Config + CLI v1
- Add config schema (YAML/JSON)
- Add CLI command:
  - input data path
  - strategy selection + params
  - execution settings
  - output path
- Add examples under `examples/`

**Deliverable:** Backtest execution from command line with config only.

### M5 — Robustness & QA
- Add edge-case tests:
  - missing data
  - flat price series
  - zero-volume bars
  - invalid params
- Add regression snapshot tests for known datasets
- Add CI workflow (lint + tests)

**Deliverable:** Reliable CI-gated baseline.

### M6 — Optional Enhancements
- Parameter sweep/optimization
- Multi-asset portfolio support
- Walk-forward analysis
- Paper-trading adapter interface
- Optional market adapter for Kalshi and/or other futures/prediction markets (simulation-first, then paper/live)

**Deliverable:** Advanced research workflow.

### M7 — Optional Market Integration (Kalshi / Futures)
- Add broker/exchange adapter interface (`submit_order`, `cancel_order`, `positions`, `fills`, `balances`)
- Implement `KalshiAdapter` behind feature flag
- Add generic `FuturesAdapter` contract for other markets
- Add dry-run/paper mode before any live mode
- Add strict risk controls:
  - max position size
  - max daily loss
  - kill-switch
  - circuit-breaker on API/data failures
- Add reconciliation job (exchange fills vs internal state)
- Add integration tests with mocked APIs

**Deliverable:** Optional execution layer that can route validated signals to Kalshi/other futures-style venues with safety controls.

---

## 6) Implementation Work Breakdown

### A. Engineering Setup
- [ ] Add `pyproject.toml`
- [ ] Add `ruff` config and rules
- [ ] Add `pytest.ini`
- [ ] Add pre-commit hooks
- [ ] Add CI pipeline (GitHub Actions)

### B. Domain Models
- [ ] Define `Candle`, `Signal`, `Order`, `Fill`, `Position`, `PortfolioState`
- [ ] Enforce typing and validation

### C. Engine
- [ ] Implement deterministic bar-by-bar loop
- [ ] Plug strategy output into execution model
- [ ] Record trades/equity timeline

### D. Strategies
- [ ] Harden base strategy contract
- [ ] MA crossover strategy
- [ ] Mean reversion strategy
- [ ] Strategy test fixtures

### E. Metrics
- [ ] Return and drawdown functions
- [ ] Risk-adjusted metrics
- [ ] Metrics test vectors

### F. Interfaces
- [ ] Config parser
- [ ] CLI runner
- [ ] Result persistence layer

### G. Documentation
- [ ] Update architecture doc diagrams/flow
- [ ] Add quickstart to README
- [ ] Add developer guide (how to add a strategy)

---

## 7) Testing Strategy

### Test Layers
- Unit tests: strategy decisions, metric formulas, execution rules
- Integration tests: full backtest run from sample dataset
- Regression tests: fixed dataset + expected outputs

### Quality Gates
- All tests pass in CI
- Lint/format checks pass
- No untyped public interfaces in core modules

---

## 8) Risks & Mitigations
- **Risk:** Lookahead bias in strategy evaluation  
  **Mitigation:** Strict bar-close signal generation and next-bar execution policy

- **Risk:** Data quality issues (missing/duplicate timestamps)  
  **Mitigation:** Data validator + fail-fast checks

- **Risk:** Metric mismatch vs expectations  
  **Mitigation:** Reference test vectors and documented formulas

- **Risk:** Scope creep into live trading too early  
  **Mitigation:** Keep Phase 1 research-only and interface-driven

---

## 9) Immediate Next Steps (This Week)
1. Add packaging/tooling (`pyproject.toml`, ruff, pytest config)
2. Implement domain models and engine contract
3. Upgrade moving average strategy to window-based logic
4. Expand tests (engine + strategy + performance metrics)
5. Add CLI/config skeleton and one runnable example

---

## 10) Definition of Done (Phase 1)
- Single command runs backtest from config
- Outputs: trade log, equity curve, metrics summary
- Tests cover critical pathways and pass in CI
- Docs enable a new contributor to add a strategy in <30 minutes
