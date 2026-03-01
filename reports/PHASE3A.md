# PHASE3A — Failure Diagnosis (Started)

## Summary
Phase 3 has started in **diagnostic mode** (3A), not full ML build.

Why: Phase 2 ended with:
- baseline real-data run: **INVALID** (insufficient trading evidence)
- validity probe run (high-turnover): **FAIL** (valid evidence, unstable collapse behavior)

## Key findings
1) **Cost sensitivity is real**
- bps cost stress degrades return as costs rise (5 -> 20 bps).

2) **Asymmetry hurts**
- asymmetric slippage case underperforms symmetric 10 bps setup.

3) **Regime weakness in stress periods**
- stress Sharpe significantly lower than calm Sharpe.

4) **Turnover tradeoff**
- low turnover fails validity evidence thresholds.
- high turnover passes validity but fails collapse threshold.

## Immediate Phase 3A actions
- Build a regime-aware diagnostic notebook/report path.
- Add EV hurdle policy candidate (edge must exceed modeled costs).
- Add turnover controls (cooldown/signal threshold) and re-run walkforward.

## Promotion criteria to Phase 3B (ML build)
- Validity PASS
- collapse_ratio < max_collapse_ratio
- Improved OOS consistency vs current baseline

See machine-readable details in `reports/phase3a_diagnosis.json`.
