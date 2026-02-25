def run_backtest(prices, strategy):
    """Run a minimal backtest and return generated signals."""
    return [strategy.on_price(p) for p in prices]
