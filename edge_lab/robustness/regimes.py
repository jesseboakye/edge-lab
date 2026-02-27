def split_regimes(prices: list[float], vol_window: int = 5) -> dict[str, list[int]]:
    """Split indices into calm vs stress by rolling absolute returns median."""
    if len(prices) < 3:
        return {"calm": list(range(len(prices))), "stress": []}

    rets = [0.0]
    for i in range(1, len(prices)):
        prev = prices[i - 1]
        rets.append(0.0 if prev == 0 else abs((prices[i] - prev) / prev))

    vols = []
    for i in range(len(prices)):
        lo = max(0, i - vol_window + 1)
        window = rets[lo : i + 1]
        vols.append(sum(window) / len(window))

    med = sorted(vols)[len(vols) // 2]
    calm = [i for i, v in enumerate(vols) if v <= med]
    stress = [i for i, v in enumerate(vols) if v > med]
    return {"calm": calm, "stress": stress}
