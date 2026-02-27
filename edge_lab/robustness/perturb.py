def add_noise(prices: list[float], eps: float = 0.001) -> list[float]:
    """Deterministic alternating perturbation for reproducible robustness tests."""
    out = []
    for i, p in enumerate(prices):
        sign = 1.0 if i % 2 == 0 else -1.0
        out.append(float(p) * (1.0 + sign * eps))
    return out
