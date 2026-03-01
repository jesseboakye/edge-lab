from .base import Strategy


class ChurnStrategy(Strategy):
    """Intentionally high-turnover strategy for gate/evidence evaluation."""

    def __init__(self):
        self._buy_next = True

    def on_price(self, _price: float) -> str:
        if self._buy_next:
            self._buy_next = False
            return "BUY"
        self._buy_next = True
        return "SELL"
