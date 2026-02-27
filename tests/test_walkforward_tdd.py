from edge_lab.execution.costs import CostModel
from edge_lab.walkforward import rolling_windows, run_walkforward


class DummyStrategy:
    def on_price(self, _price):
        return "HOLD"


def strategy_factory(_cfg):
    return DummyStrategy()


def test_rolling_windows_count():
    windows = rolling_windows(n=20, train=10, test=5, step=5)
    assert windows == [(0, 10, 10, 15), (5, 15, 15, 20)]


def test_run_walkforward_returns_window_results():
    prices = [100 + i for i in range(30)]
    out = run_walkforward(
        prices=prices,
        train_size=10,
        test_size=5,
        step=5,
        strategy_factory=strategy_factory,
        strategy_config={"name": "dummy", "params": {}},
        initial_cash=1000.0,
        cost_model=CostModel(mode="bps", fee_bps=5.0),
        risk_free_rate=0.0,
    )
    assert out["window_count"] == 4
    assert len(out["windows"]) == 4
    assert "mean_total_return" in out["aggregate"]
    assert "collapse_ratio" in out["aggregate"]
