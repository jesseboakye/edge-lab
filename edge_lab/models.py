from dataclasses import dataclass
from enum import Enum


class Signal(str, Enum):
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"


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
