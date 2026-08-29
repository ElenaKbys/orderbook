"""Core value types for the order book.

These are deliberately dumb containers. All behaviour lives in `book.py` — keeping the
types inert makes them trivial to construct in tests and impossible to get subtly wrong.

Prices are integer ticks, not floats. Real exchanges quote on a discrete grid, and using
integers here removes a whole class of floating-point equality bugs from the matching logic.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from itertools import count


class Side(Enum):
    """Which side of the book an order sits on."""

    BUY = "buy"
    SELL = "sell"

    @property
    def opposite(self) -> "Side":
        return Side.SELL if self is Side.BUY else Side.BUY


class OrderType(Enum):
    """Limit orders rest in the book; market orders never do."""

    LIMIT = "limit"
    MARKET = "market"


_order_ids = count(1)


@dataclass
class Order:
    """A single order.

    Attributes
    ----------
    side:
        BUY or SELL.
    quantity:
        Remaining unfilled size. Mutated as the order fills.
    price:
        Integer tick. ``None`` for market orders, which have no limit price.
    order_type:
        LIMIT or MARKET.
    timestamp:
        Arrival sequence number. Lower means earlier, which is what time priority
        is decided on. The simulation supplies this; it is not wall-clock time.
    order_id:
        Unique, auto-assigned.
    """

    side: Side
    quantity: int
    price: int | None = None
    order_type: OrderType = OrderType.LIMIT
    timestamp: int = 0
    order_id: int = field(default_factory=lambda: next(_order_ids))

    def __post_init__(self) -> None:
        if self.quantity <= 0:
            raise ValueError(f"quantity must be positive, got {self.quantity}")
        if self.order_type is OrderType.LIMIT and self.price is None:
            raise ValueError("limit orders require a price")
        if self.order_type is OrderType.MARKET and self.price is not None:
            raise ValueError("market orders must not carry a price")

    @property
    def is_filled(self) -> bool:
        return self.quantity == 0


@dataclass(frozen=True)
class Trade:
    """An execution between two orders.

    ``price`` is the resting order's price, not the incoming order's. This is the
    convention exchanges use: the order that was already in the book set the terms,
    and the incoming order accepted them.
    """

    price: int
    quantity: int
    resting_order_id: int
    incoming_order_id: int
    timestamp: int

    @property
    def notional(self) -> int:
        return self.price * self.quantity
