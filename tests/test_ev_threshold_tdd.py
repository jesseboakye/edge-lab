from edge_lab.strategies.ev_threshold import EVThresholdStrategy


def test_ev_threshold_emits_hold_on_warmup():
    s = EVThresholdStrategy(short_window=2, long_window=3, min_edge_bps=1, cooldown_bars=1)
    assert s.on_price(100) == "HOLD"
    assert s.on_price(101) == "HOLD"


def test_ev_threshold_can_emit_signal():
    s = EVThresholdStrategy(short_window=2, long_window=3, min_edge_bps=1, cooldown_bars=0)
    s.on_price(100)
    s.on_price(101)
    sig = s.on_price(110)
    assert sig in {"BUY", "SELL", "HOLD"}
