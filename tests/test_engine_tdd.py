from edge_lab.backtest.engine import run_backtest
from edge_lab.strategies.base import Strategy


class SequenceStrategy(Strategy):
    def __init__(self, signals):
        self.signals = list(signals)
        self.i = 0

    def on_price(self, price):
        signal = self.signals[self.i] if self.i < len(self.signals) else "HOLD"
        self.i += 1
        return signal


def test_run_backtest_keeps_simple_signal_mode():
    strategy = SequenceStrategy(["BUY", "HOLD", "SELL"])
    signals = run_backtest([100, 101, 102], strategy)
    assert signals == ["BUY", "HOLD", "SELL"]


def test_run_backtest_detailed_applies_fees_and_slippage():
    strategy = SequenceStrategy(["BUY", "HOLD", "SELL"])
    result = run_backtest(
        [100.0, 101.0, 102.0],
        strategy,
        detailed=True,
        initial_cash=1000.0,
        fee_bps=10,      # 0.10%
        slippage_bps=5,  # 0.05%
    )

    assert result["signals"] == ["BUY", "HOLD", "SELL"]
    assert len(result["trades"]) == 2
    assert result["final_position"] == 0
    # Costs should reduce ending equity below naive +2 gain
    assert result["final_equity"] < 1002.0
    assert result["final_equity"] > 999.0


def test_run_backtest_detailed_default_fee_is_5_bps_per_fill():
    strategy = SequenceStrategy(["BUY", "SELL"])
    result = run_backtest(
        [100.0, 100.0],
        strategy,
        detailed=True,
        initial_cash=1000.0,
        slippage_bps=0,
    )

    # Two fills with 5 bps each on $100 notional => total fee = $0.10
    assert round(result["final_equity"], 6) == 999.9
