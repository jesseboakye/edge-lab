from .base import Strategy


class EVThresholdStrategy(Strategy):
    """MA-spread proxy with EV hurdle + cooldown for turnover control."""

    def __init__(self, short_window: int = 20, long_window: int = 50, min_edge_bps: float = 8.0, cooldown_bars: int = 3):
        if short_window <= 0 or long_window <= 0 or short_window >= long_window:
            raise ValueError("Invalid windows")
        self.short_window = short_window
        self.long_window = long_window
        self.min_edge_bps = float(min_edge_bps)
        self.cooldown_bars = int(cooldown_bars)
        self._prices: list[float] = []
        self._cooldown_left = 0

    def on_price(self, price: float) -> str:
        self._prices.append(float(price))
        if len(self._prices) < self.long_window:
            return "HOLD"

        short_avg = sum(self._prices[-self.short_window :]) / self.short_window
        long_avg = sum(self._prices[-self.long_window :]) / self.long_window
        edge_bps = ((short_avg - long_avg) / long_avg) * 10_000 if long_avg else 0.0

        if self._cooldown_left > 0:
            self._cooldown_left -= 1
            return "HOLD"

        if edge_bps > self.min_edge_bps:
            self._cooldown_left = self.cooldown_bars
            return "BUY"
        if edge_bps < -self.min_edge_bps:
            self._cooldown_left = self.cooldown_bars
            return "SELL"
        return "HOLD"
