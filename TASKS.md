# TASKS

## Backbone (Phase 1) — Engineering First
- [x] Lock v1 assumptions (engine/costs/sharpe)
- [x] Make tests runnable in environment (local Python + venv + pytest)
- [x] Implement initial engine/strategy/metrics with TDD
- [x] Add domain models (`Candle`, `Signal`, `Order`, `Fill`, `PortfolioState`)
- [x] Add config schema for reproducible runs
- [x] Add CLI entrypoint for config-driven backtests
- [x] Add walk-forward validation module + tests
- [ ] Add deterministic artifact outputs (metrics/trades/equity)

## Robustness (Phase 2)
- [ ] Cost stress tests (5/10/20 bps)
- [ ] Regime split evaluation (crash vs low-vol periods)
- [ ] Feature perturbation/noise tests
- [ ] Rolling-window stability report (explicit collapse flag)

## Deferred (Post-Phase 2)
- [ ] Optional Kalshi/futures adapter work
