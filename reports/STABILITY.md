# STABILITY

## Precommitted collapse criteria
- Sharpe floor per window: `0.0`
- Maximum allowed collapse ratio: `0.5`
- Collapse definition: window is collapsed if `sharpe < sharpe_floor`

## Walk-forward summary
- Windows: `2`
- Collapse count: `1`
- Collapse ratio: `0.5`
- Collapse pass: `true` (ratio <= 0.5)

## Notes
- One window failed Sharpe floor and one passed.
- Stability is currently at threshold, not comfortably above it.
- See `reports/robustness_walkforward.json` for full per-window detail.
