from edge_lab.risk.sizing import fractional_kelly_fraction, target_position_qty


def test_fractional_kelly_positive_edge():
    frac = fractional_kelly_fraction(prob_win=0.6, payoff_ratio=1.0, kelly_fraction=0.5)
    assert frac > 0


def test_target_position_qty_respects_cap():
    qty = target_position_qty(equity=1000, price=100, fraction=0.9, max_exposure_frac=0.2)
    assert round(qty, 6) == 2.0
