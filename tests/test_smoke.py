from edge_lab.backtest.engine import run_backtest
from edge_lab.strategies.moving_average import MovingAverageStrategy


def test_smoke_backtest_runs():
    strategy = MovingAverageStrategy(threshold=10)
    signals = run_backtest([9, 10, 11], strategy)
    assert signals == ["SELL", "HOLD", "BUY"]
