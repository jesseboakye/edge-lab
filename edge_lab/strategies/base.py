class Strategy:
    """Base strategy contract."""

    def on_price(self, price):
        raise NotImplementedError
