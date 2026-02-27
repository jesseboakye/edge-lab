from dataclasses import dataclass


@dataclass(frozen=True)
class CostModel:
    mode: str = "bps"  # bps | per_unit
    fee_bps: float = 5.0
    fee_per_unit: float = 0.0
    spread_per_unit: float = 0.0
    slippage_entry_bps: float = 0.0
    slippage_exit_bps: float = 0.0


def _slippage_rate(bps: float) -> float:
    return bps / 10_000.0


def apply_execution_costs(price: float, side: str, qty: float, cost: CostModel, is_entry: bool) -> tuple[float, float]:
    """Return (execution_price, fee).

    - mode='bps': fee = notional * fee_bps
    - mode='per_unit': fee = qty * fee_per_unit
    Spread widens buy/sell price symmetrically by spread/2.
    Slippage can be asymmetric for entry/exit.
    """
    px = float(price)
    q = float(qty)

    half_spread = float(cost.spread_per_unit) / 2.0
    slip_bps = cost.slippage_entry_bps if is_entry else cost.slippage_exit_bps
    slip_rate = _slippage_rate(slip_bps)

    if side == "BUY":
        exec_price = (px + half_spread) * (1.0 + slip_rate)
    elif side == "SELL":
        exec_price = (px - half_spread) * (1.0 - slip_rate)
    else:
        exec_price = px

    if cost.mode == "bps":
        fee = abs(exec_price * q) * (float(cost.fee_bps) / 10_000.0)
    elif cost.mode == "per_unit":
        fee = abs(q) * float(cost.fee_per_unit)
    else:
        raise ValueError(f"Unsupported cost mode: {cost.mode}")

    return exec_price, fee
