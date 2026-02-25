from .base import Strategy


class MovingAverageStrategy(Strategy):
    def __init__(self, short_window: int = 5, long_window: int = 20):
        if short_window <= 0 or long_window <= 0:
            raise ValueError("Windows must be positive")
        if short_window >= long_window:
            raise ValueError("short_window must be < long_window")

        self.short_window = short_window
        self.long_window = long_window
        self._prices = []

    def on_price(self, price: float) -> str:
        self._prices.append(float(price))

        if len(self._prices) < self.long_window:
            return "HOLD"

        short_avg = sum(self._prices[-self.short_window :]) / self.short_window
        long_avg = sum(self._prices[-self.long_window :]) / self.long_window

        if short_avg > long_avg:
            return "BUY"
        if short_avg < long_avg:
            return "SELL"
        return "HOLD"
