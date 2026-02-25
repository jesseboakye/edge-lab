from .base import Strategy


class MovingAverageStrategy(Strategy):
    def __init__(self, threshold=0):
        self.threshold = threshold

    def on_price(self, price):
        if price > self.threshold:
            return "BUY"
        if price < self.threshold:
            return "SELL"
        return "HOLD"
