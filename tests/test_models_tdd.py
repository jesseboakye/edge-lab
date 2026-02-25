from edge_lab.models import Candle, Signal


def test_candle_mid_price():
    c = Candle(ts="2026-01-01", open=100, high=110, low=90, close=105, volume=10)
    assert c.mid_price == 100.0


def test_candle_rejects_invalid_high_low():
    try:
        Candle(ts="2026-01-01", open=100, high=80, low=90, close=95, volume=1)
    except ValueError as exc:
        assert "high must be >= low" in str(exc)
        return
    assert False, "Expected ValueError"


def test_signal_values_stable():
    assert Signal.BUY.value == "BUY"
    assert Signal.SELL.value == "SELL"
    assert Signal.HOLD.value == "HOLD"
