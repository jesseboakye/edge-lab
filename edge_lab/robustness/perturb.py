def add_noise(prices: list[float], eps: float = 0.001, seed: int = 11) -> list[float]:
    """Deterministic pseudo-random perturbation (LCG) for reproducibility."""
    out = []
    state = int(seed) & 0x7FFFFFFF
    for p in prices:
        state = (1103515245 * state + 12345) & 0x7FFFFFFF
        u = state / 0x7FFFFFFF  # [0,1]
        z = (u * 2.0) - 1.0      # [-1,1]
        out.append(float(p) * (1.0 + z * eps))
    return out
