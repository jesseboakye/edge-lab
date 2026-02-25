# Architecture

## Components
- `edge_lab.backtest.engine`: simulation runner
- `edge_lab.strategies.*`: trading logic
- `edge_lab.metrics.performance`: portfolio metrics

## Flow
1. Load price series
2. Generate signals from strategy
3. Execute simulated trades
4. Compute metrics
