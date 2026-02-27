from typing import Any

from edge_lab.execution.costs import CostModel, apply_execution_costs


def run_backtest(
    prices,
    strategy,
    *,
    detailed: bool = False,
    initial_cash: float = 0.0,
    fee_bps: float = 5.0,
    slippage_bps: float = 0.0,
    cost_model: CostModel | None = None,
    qty: float = 1.0,
) -> Any:
    """Run a minimal backtest.

    Default behavior is backwards-compatible and returns generated signals.
    Set detailed=True to return trade/equity details.

    v1 assumptions:
    - Long/flat only
    - BUY opens only when flat; SELL closes only when long
    """
    signals = [strategy.on_price(p) for p in prices]
    if not detailed:
        return signals

    cost = cost_model or CostModel(
        mode="bps",
        fee_bps=fee_bps,
        slippage_entry_bps=slippage_bps,
        slippage_exit_bps=slippage_bps,
    )

    cash = float(initial_cash)
    position = 0.0
    equity_curve = []
    trades = []

    for price, signal in zip(prices, signals):
        price = float(price)

        if signal == "BUY" and position == 0:
            exec_price, fee = apply_execution_costs(price, "BUY", qty, cost, is_entry=True)
            cash -= (exec_price * qty) + fee
            position = qty
            trades.append({"side": "BUY", "price": exec_price, "fee": fee, "qty": qty})

        elif signal == "SELL" and position > 0:
            exec_price, fee = apply_execution_costs(price, "SELL", position, cost, is_entry=False)
            cash += (exec_price * position) - fee
            trades.append({"side": "SELL", "price": exec_price, "fee": fee, "qty": position})
            position = 0.0

        equity = cash + (position * price)
        equity_curve.append(equity)

    return {
        "signals": signals,
        "trades": trades,
        "equity_curve": equity_curve,
        "final_position": position,
        "final_equity": equity_curve[-1] if equity_curve else initial_cash,
        "cost_mode": cost.mode,
    }
