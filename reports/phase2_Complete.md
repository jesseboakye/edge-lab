# phase2_Complete

Phase 2 robustness outputs generated:
- `reports/robustness_cost_stress.json`
- `reports/robustness_regime_split.json`
- `reports/robustness_perturbation.json`
- `reports/STABILITY.md`

## Coverage vs requested goals
- Cost stress: 5/10/20 bps + asymmetry toggle case included
- Regime split: realized-vol quantile + drawdown stress definitions implemented
- Feature perturbation: systematic noise levels + seeds + fragility index
- Rolling stability: precommitted collapse criteria + summary
- Vaulted holdout: defined/locked via metadata tags (`holdout_tag`)
- Repro metadata: config hash, commit, seeds, dataset id

## Reproducibility metadata fields now present in reports
- `config_hash`
- `git_commit`
- `seeds`
- `dataset_id`
- `holdout_tag`
- `run_timestamp_utc`
