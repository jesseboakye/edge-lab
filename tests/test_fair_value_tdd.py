from edge_lab.models import fair_value_quote, probability_to_fair_price


def test_probability_to_fair_price_binary_contract():
    assert probability_to_fair_price(0.7, payout_if_up=1.0, payout_if_down=0.0) == 0.7


def test_fair_value_quote_edge():
    q = fair_value_quote(0.65, market_price=0.60)
    assert round(q.fair_price, 6) == 0.65
    assert round(q.edge_vs_market, 6) == 0.05
