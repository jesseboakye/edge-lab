# Report JSON Schemas (Minimal)

## Backtest Report (`edge_lab.backtest.v1`)
```json
{
  "schema": "edge_lab.backtest.v1",
  "final_equity": 1000.0,
  "cost_mode": "bps|per_unit",
  "metrics": {
    "total_return": 0.0,
    "max_drawdown": 0.0,
    "sharpe": 0.0
  },
  "trades": [],
  "equity_curve": []
}
```

## Walk-Forward Report (`edge_lab.walkforward.v1`)
```json
{
  "schema": "edge_lab.walkforward.v1",
  "window_count": 0,
  "windows": [
    {
      "train": [0, 100],
      "test": [100, 120],
      "total_return": 0.0,
      "sharpe": 0.0,
      "collapsed": false
    }
  ],
  "aggregate": {
    "mean_total_return": 0.0,
    "mean_sharpe": 0.0,
    "collapse_count": 0,
    "collapse_ratio": 0.0
  }
}
```

## Cost Stress Report (`edge_lab.cost_stress.v1`)
```json
{
  "schema": "edge_lab.cost_stress.v1",
  "results": [
    {
      "mode": "bps|per_unit",
      "fee_bps": 5.0,
      "fee_per_unit": 0.0,
      "final_equity": 1000.0,
      "metrics": {
        "total_return": 0.0,
        "max_drawdown": 0.0,
        "sharpe": 0.0
      }
    }
  ]
}
```
