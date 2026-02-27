# Folder Structure (Targeted)

- `edge_lab/models.py` — domain models + fair value conversion
- `edge_lab/backtest/engine.py` — simulation loop, cost-engine aware
- `edge_lab/execution/costs.py` — unified cost model + pricing/fees
- `edge_lab/risk/sizing.py` — fractional Kelly + exposure cap
- `edge_lab/config/schema.py` — YAML/JSON config parsing
- `edge_lab/walkforward.py` — rolling OOS validation + collapse stats
- `edge_lab/cli.py` — backtest, walkforward, cost-stress commands
- `reports/*.json` — run outputs with schema tags

## Minimal Module Interfaces

### Fair Value
- `probability_to_fair_price(probability_up, payout_if_up=1.0, payout_if_down=0.0) -> float`
- `fair_value_quote(probability_up, market_price, payout_if_up=1.0, payout_if_down=0.0) -> FairValueQuote`

### Cost Engine
- `CostModel(mode, fee_bps, fee_per_unit, spread_per_unit, slippage_entry_bps, slippage_exit_bps)`
- `apply_execution_costs(price, side, qty, cost, is_entry) -> (execution_price, fee)`

### Backtest
- `run_backtest(..., cost_model: CostModel | None = None, qty: float = 1.0)`

### Sizing
- `fractional_kelly_fraction(prob_win, payoff_ratio, kelly_fraction=0.25) -> float`
- `target_position_qty(equity, price, fraction, max_exposure_frac=0.2) -> float`
