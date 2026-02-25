from edge_lab.backtest.engine import run_backtest
from edge_lab.strategies.moving_average import MovingAverageStrategy


def test_smoke_backtest_runs():
    strategy = MovingAverageStrategy(short_window=2, long_window=3)
    signals = run_backtest([1, 2, 3, 4, 5], strategy)
    assert signals == ["HOLD", "HOLD", "BUY", "BUY", "BUY"]
