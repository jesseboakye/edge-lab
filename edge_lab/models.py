from dataclasses import dataclass
from enum import Enum


class Signal(str, Enum):
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"


@dataclass(frozen=True)
class FairValueQuote:
    probability_up: float
    fair_price: float
    edge_vs_market: float
    expected_value_per_unit: float


def probability_to_fair_price(probability_up: float, payout_if_up: float = 1.0, payout_if_down: float = 0.0) -> float:
    p = max(0.0, min(1.0, float(probability_up)))
    return p * float(payout_if_up) + (1.0 - p) * float(payout_if_down)


def fair_value_quote(probability_up: float, market_price: float, payout_if_up: float = 1.0, payout_if_down: float = 0.0) -> FairValueQuote:
    fair = probability_to_fair_price(probability_up, payout_if_up, payout_if_down)
    edge = fair - float(market_price)
    return FairValueQuote(
        probability_up=float(probability_up),
        fair_price=fair,
        edge_vs_market=edge,
        expected_value_per_unit=edge,
    )


@dataclass(frozen=True)
class Candle:
    ts: str
    open: float
    high: float
    low: float
    close: float
    volume: float

    def __post_init__(self):
        if self.high < self.low:
            raise ValueError("high must be >= low")

    @property
    def mid_price(self) -> float:
        return (float(self.high) + float(self.low)) / 2.0


@dataclass(frozen=True)
class Order:
    ts: str
    side: Signal
    qty: float


@dataclass(frozen=True)
class Fill:
    ts: str
    side: Signal
    qty: float
    price: float
    fee: float


@dataclass(frozen=True)
class Position:
    qty: float


@dataclass(frozen=True)
class PortfolioState:
    cash: float
    position_qty: float
    equity: float
