# STABILITY

## Validity checks
- min_windows: required `8`, observed `2` → **FAIL**
- min_oos_days: required `120`, observed `10` → **FAIL**
- min_trades_total: required `200`, observed `3` → **FAIL**
- min_trades_per_window: required `20`, observed `[2, 1]` → **FAIL**

## Collapse evaluation
- collapse_ratio: `0.5`
- max_collapse_ratio: `0.5`
- strict rule: collapse_ratio < max_collapse_ratio
- collapse_pass: **false**

## Final status
- status: **INVALID**
- promotable: **false**
- reason codes:
  - `INSUFFICIENT_WINDOWS`
  - `INSUFFICIENT_OOS_DAYS`
  - `INSUFFICIENT_TRADES_TOTAL`
  - `INSUFFICIENT_TRADES_PER_WINDOW`

Notes:
- Collapse metrics are computed, but promotion is blocked when validity fails.
- JSON source: `reports/robustness_walkforward.json`
