class Strategy:
    """Base strategy contract."""

    def on_price(self, price: float) -> str:
        """Return one of BUY, SELL, HOLD."""
        raise NotImplementedError
