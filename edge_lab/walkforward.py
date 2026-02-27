from statistics import mean
from typing import Any, Callable

from edge_lab.backtest.engine import run_backtest
from edge_lab.execution.costs import CostModel
from edge_lab.metrics.performance import sharpe_ratio, total_return


def rolling_windows(n: int, train: int, test: int, step: int) -> list[tuple[int, int, int, int]]:
    windows: list[tuple[int, int, int, int]] = []
    start = 0
    while True:
        train_start = start
        train_end = train_start + train
        test_start = train_end
        test_end = test_start + test
        if test_end > n:
            break
        windows.append((train_start, train_end, test_start, test_end))
        start += step
    return windows


def _period_returns(equity_curve: list[float]) -> list[float]:
    if len(equity_curve) < 2:
        return []
    out = []
    for i in range(1, len(equity_curve)):
        prev = equity_curve[i - 1]
        cur = equity_curve[i]
        out.append(0.0 if prev == 0 else (cur - prev) / prev)
    return out


def run_walkforward(
    *,
    prices: list[float],
    train_size: int,
    test_size: int,
    step: int,
    strategy_factory: Callable[[dict[str, Any]], Any],
    strategy_config: dict[str, Any],
    initial_cash: float,
    cost_model: CostModel,
    risk_free_rate: float,
    collapse_sharpe_floor: float = 0.0,
) -> dict[str, Any]:
    windows = rolling_windows(n=len(prices), train=train_size, test=test_size, step=step)

    rows = []
    for train_start, train_end, test_start, test_end in windows:
        _train_prices = prices[train_start:train_end]  # reserved for future fit stage
        test_prices = prices[test_start:test_end]

        strategy = strategy_factory(strategy_config)
        result = run_backtest(
            test_prices,
            strategy,
            detailed=True,
            initial_cash=initial_cash,
            cost_model=cost_model,
        )
        returns = _period_returns(result["equity_curve"])

        row = {
            "train": [train_start, train_end],
            "test": [test_start, test_end],
            "oos_days": (test_end - test_start),
            "trade_count": len(result["trades"]),
            "final_equity": result["final_equity"],
            "total_return": total_return(result["equity_curve"]),
            "sharpe": sharpe_ratio(returns, risk_free_rate=risk_free_rate),
        }
        row["collapsed"] = row["sharpe"] < collapse_sharpe_floor
        rows.append(row)

    mean_total_return = mean([r["total_return"] for r in rows]) if rows else 0.0
    mean_sharpe = mean([r["sharpe"] for r in rows]) if rows else 0.0
    collapse_count = sum(1 for r in rows if r["collapsed"])
    oos_days_total = sum(r["oos_days"] for r in rows)
    trades_total = sum(r["trade_count"] for r in rows)

    return {
        "window_count": len(rows),
        "windows": rows,
        "aggregate": {
            "mean_total_return": mean_total_return,
            "mean_sharpe": mean_sharpe,
            "collapse_count": collapse_count,
            "collapse_ratio": (collapse_count / len(rows)) if rows else 0.0,
            "oos_days_total": oos_days_total,
            "trades_total": trades_total,
        },
    }
