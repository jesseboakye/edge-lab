from edge_lab.metrics.performance import max_drawdown, sharpe_ratio, total_return


def test_total_return_basic():
    assert total_return([100, 110]) == 0.1


def test_max_drawdown_basic():
    dd = max_drawdown([100, 120, 90, 130])
    # drawdown from 120 -> 90 = -25%
    assert round(dd, 6) == -0.25


def test_sharpe_ratio_zero_for_flat_returns():
    assert sharpe_ratio([0.0, 0.0, 0.0]) == 0.0


def test_sharpe_ratio_positive_for_positive_mean_returns():
    value = sharpe_ratio([0.01, 0.02, 0.015, 0.012])
    assert value > 0


def test_sharpe_ratio_uses_sample_std_ddof_1():
    # mean=2, sample std=1, periods_per_year=1 => sharpe=2
    value = sharpe_ratio([1.0, 2.0, 3.0], periods_per_year=1)
    assert round(value, 6) == 2.0
