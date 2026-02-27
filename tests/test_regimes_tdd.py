from edge_lab.robustness.regimes import split_regimes


def test_split_regimes_returns_calm_and_stress():
    out = split_regimes([100, 101, 99, 105, 104, 110])
    assert "calm" in out and "stress" in out
    assert len(out["calm"]) + len(out["stress"]) == 6
