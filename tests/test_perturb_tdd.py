from edge_lab.robustness.perturb import add_noise


def test_add_noise_is_seeded_and_reproducible():
    prices = [100.0, 100.0, 100.0]
    a = add_noise(prices, eps=0.01, seed=7)
    b = add_noise(prices, eps=0.01, seed=7)
    c = add_noise(prices, eps=0.01, seed=9)
    assert a == b
    assert a != c
