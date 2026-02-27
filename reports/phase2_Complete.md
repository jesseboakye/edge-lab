# phase2_Complete

Phase 2 robustness outputs generated:
- `reports/robustness_cost_stress.json`
- `reports/robustness_regime_split.json`
- `reports/robustness_perturbation.json`
- `reports/STABILITY.md`

Vault enforcement deliverables:
- `reports/phase2_freeze.json`
- `reports/holdout_ledger.json`

## Stability gate semantics (updated)
- Gate now supports final status states: `PASS` / `FAIL` / `INVALID`
- Validity thresholds are config-governed:
  - `min_windows` (default 8)
  - `min_oos_days` (default 120)
  - `min_trades_total` (default 200)
  - `min_trades_per_window` (default 20)
- If any validity check fails, status is `INVALID` and `promotable=false` regardless of collapse ratio
- Collapse pass rule is strict: `collapse_ratio < max_collapse_ratio`
- JSON output includes: `validity`, `status`, `promotable`

Current baseline status: **INVALID** (insufficient evidence volume), so not promotable.
