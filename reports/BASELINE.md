# Baseline Report (Backbone v1)

Generated from:
- `configs/baseline.yaml`
- backtest + walk-forward CLI runs

## Test Status
- `17 passed` via `python -m pytest -q`

## Backtest (single run)
- Final equity: `1002.7410`
- Total return: `0.2741%`
- Max drawdown: `-0.2099%`
- Sharpe (sample std, sqrt(252), rf per-period): `2.9589`

## Walk-Forward (train=10, test=5, step=5)
- Windows: `2`
- Mean total return: `0.0421%`
- Mean Sharpe: `2.2831`

Per-window:
1. train `[0,10]`, test `[10,15]` → return `-0.1106%`, Sharpe `-8.4694`
2. train `[5,15]`, test `[15,20]` → return `0.1947%`, Sharpe `13.0356`

## Notes
- v1 assumptions locked:
  - Long/flat only (1 unit)
  - Fixed cost model: 5 bps per fill, no min ticket fee
  - No spread/impact modeling in v1
- No-leakage posture for v1:
  - Walk-forward evaluates each test window separately and re-instantiates strategy per window.
  - Current strategy has no train-time fitting; future fitted transforms/models must be fit on train window only, then applied to test.
