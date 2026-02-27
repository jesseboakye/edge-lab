# STABILITY

## Precommitted collapse criteria
- Sharpe floor per window: `0.0`
- Maximum allowed collapse ratio: `0.5`
- Collapse definition: window collapsed if `sharpe < sharpe_floor`

## Walk-forward summary (dev mode)
- Windows: `2`
- Collapse count: `1`
- Collapse ratio: `0.5`
- Collapse pass: `true`

## Vault workflow status
- Holdout guardrail mode implemented: `--mode {dev,final}`
- Dev mode hard-excludes holdout overlap by config contract
- Final mode requires freeze file + ledger append
