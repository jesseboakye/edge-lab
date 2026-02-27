def fractional_kelly_fraction(prob_win: float, payoff_ratio: float, kelly_fraction: float = 0.25) -> float:
    """Return fraction of capital to allocate.

    Full Kelly for binary payoff b: f* = p - (1-p)/b
    Fractional Kelly scales by kelly_fraction and floors at 0.
    """
    p = float(prob_win)
    b = float(payoff_ratio)
    if b <= 0:
        return 0.0
    full = p - (1.0 - p) / b
    return max(0.0, full * float(kelly_fraction))


def target_position_qty(*, equity: float, price: float, fraction: float, max_exposure_frac: float = 0.2) -> float:
    capped = min(max(float(fraction), 0.0), float(max_exposure_frac))
    if price <= 0:
        return 0.0
    dollars = float(equity) * capped
    return dollars / float(price)
