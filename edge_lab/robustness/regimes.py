def _rolling_abs_returns(prices: list[float], vol_window: int) -> list[float]:
    rets = [0.0]
    for i in range(1, len(prices)):
        prev = prices[i - 1]
        rets.append(0.0 if prev == 0 else abs((prices[i] - prev) / prev))
    vols = []
    for i in range(len(prices)):
        lo = max(0, i - vol_window + 1)
        w = rets[lo : i + 1]
        vols.append(sum(w) / len(w))
    return vols


def _drawdown_flags(prices: list[float], drawdown_thresh: float = -0.02) -> list[bool]:
    if not prices:
        return []
    peak = prices[0]
    out = []
    for p in prices:
        peak = max(peak, p)
        dd = 0.0 if peak == 0 else (p - peak) / peak
        out.append(dd <= drawdown_thresh)
    return out


def split_regimes(prices: list[float], vol_window: int = 5, q_stress: float = 0.75, drawdown_thresh: float = -0.02) -> dict[str, list[int]]:
    """Explicit regime definitions using vol quantile + drawdown stress.

    stress if rolling vol >= q_stress quantile OR drawdown stress flag true.
    calm otherwise.
    """
    if len(prices) < 3:
        return {"calm": list(range(len(prices))), "stress": []}

    vols = _rolling_abs_returns(prices, vol_window)
    sorted_vols = sorted(vols)
    idx = min(len(sorted_vols) - 1, max(0, int(q_stress * (len(sorted_vols) - 1))))
    qv = sorted_vols[idx]
    dd_stress = _drawdown_flags(prices, drawdown_thresh=drawdown_thresh)

    calm, stress = [], []
    for i, v in enumerate(vols):
        is_stress = (v >= qv) or dd_stress[i]
        (stress if is_stress else calm).append(i)
    return {"calm": calm, "stress": stress}
