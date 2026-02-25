from typing import Any


def run_backtest(
    prices,
    strategy,
    *,
    detailed: bool = False,
    initial_cash: float = 0.0,
    fee_bps: float = 5.0,
    slippage_bps: float = 0.0,
) -> Any:
    """Run a minimal backtest.

    Default behavior is backwards-compatible and returns generated signals.
    Set detailed=True to return trade/equity details.

    v1 assumptions:
    - Long/flat only, one unit position sizing
    - BUY opens only when flat; SELL closes only when long
    - Default fee is 5 bps on each executed notional (entry + exit)
    """
    signals = [strategy.on_price(p) for p in prices]
    if not detailed:
        return signals

    fee_rate = fee_bps / 10_000
    slip_rate = slippage_bps / 10_000

    cash = float(initial_cash)
    position = 0
    equity_curve = []
    trades = []

    for price, signal in zip(prices, signals):
        price = float(price)

        if signal == "BUY" and position == 0:
            exec_price = price * (1 + slip_rate)
            fee = exec_price * fee_rate
            cash -= exec_price + fee
            position = 1
            trades.append({"side": "BUY", "price": exec_price, "fee": fee})

        elif signal == "SELL" and position == 1:
            exec_price = price * (1 - slip_rate)
            fee = exec_price * fee_rate
            cash += exec_price - fee
            position = 0
            trades.append({"side": "SELL", "price": exec_price, "fee": fee})

        equity = cash + (position * price)
        equity_curve.append(equity)

    return {
        "signals": signals,
        "trades": trades,
        "equity_curve": equity_curve,
        "final_position": position,
        "final_equity": equity_curve[-1] if equity_curve else initial_cash,
    }
