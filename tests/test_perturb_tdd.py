from edge_lab.robustness.perturb import add_noise


def test_add_noise_changes_series_deterministically():
    prices = [100.0, 100.0, 100.0]
    out = add_noise(prices, eps=0.01)
    assert out == [101.0, 99.0, 101.0]
