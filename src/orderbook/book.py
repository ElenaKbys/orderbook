"""The matching engine.

TO IMPLEMENT. Every method below is specified in the docstring and pinned by a test in
`tests/test_book.py`. Work top to bottom: `best_bid`/`best_ask` first, then `add_limit_order`,
then `add_market_order`, then `cancel`. Remove the matching `xfail` marker from the test as
each one starts passing.

The one invariant that matters
------------------------------
**The book is never crossed.** After any operation, ``best_bid < best_ask``. If a buy order
arrives priced at or above the best ask, it must trade rather than rest. Nearly every bug in a
matching engine is a violation of this, so `_assert_not_crossed` is called after every mutation
and you should leave it there.

Price-time priority
-------------------
Among resting orders, the one that fills first is:

1. the one at the **best price** — highest for bids, lowest for asks; then
2. among equal prices, the one that **arrived first**.

The data structure follows directly: a dict from price to a FIFO queue of orders. Best price
is a min/max over the keys; time priority is the queue order. That is why `deque` is used and
why orders are always appended to the right and popped from the left.
"""

from __future__ import annotations

from collections import deque

from .orders import Order, OrderType, Side, Trade


class OrderBook:
    """A single-asset limit order book with price-time priority."""

    def __init__(self) -> None:
        # price -> FIFO queue of resting orders at that price
        self.bids: dict[int, deque[Order]] = {}
        self.asks: dict[int, deque[Order]] = {}
        # every trade, in order
        self.trades: list[Trade] = []
        # every event (order added, cancelled, traded) for later analysis
        self.event_log: list[dict] = []
        self._orders_by_id: dict[int, Order] = {}
        self._clock = 0

    # ------------------------------------------------------------------ queries

    def best_bid(self) -> int | None:
        """Highest price anyone is willing to buy at, or None if there are no bids.

        Remember to ignore price levels whose queue has been emptied but not removed.
        Simplest fix: delete the key whenever its queue becomes empty, so `self.bids`
        only ever holds non-empty levels. Then this is just `max(self.bids)`.
        """
        raise NotImplementedError

    def best_ask(self) -> int | None:
        """Lowest price anyone is willing to sell at, or None if there are no asks."""
        raise NotImplementedError

    def spread(self) -> int | None:
        """best_ask - best_bid, or None if either side is empty."""
        raise NotImplementedError

    def mid(self) -> float | None:
        """Midpoint of the spread, or None if either side is empty.

        This is the reference price the impact measurement is defined against, so it is
        worth being careful: it is a float even though prices are integer ticks.
        """
        raise NotImplementedError

    def depth_at(self, side: Side, price: int) -> int:
        """Total resting quantity on `side` at exactly `price`. Zero if the level is empty."""
        raise NotImplementedError

    # ------------------------------------------------------------------ mutations

    def add_limit_order(self, order: Order) -> list[Trade]:
        """Submit a limit order. Returns the trades it generated, possibly empty.

        Two cases:

        * **It crosses.** A buy priced >= best_ask (or a sell priced <= best_bid) must
          execute immediately against the resting side, consuming price levels from the
          best outward, and within a level in arrival order. Keep going while the order
          still has quantity AND the next level is still acceptable at its limit price.
        * **It does not cross, or has quantity left over.** The remainder rests: append it
          to the queue at its own price, creating the level if needed.

        Trades print at the *resting* order's price (see `Trade`).
        """
        raise NotImplementedError

    def add_market_order(self, order: Order) -> list[Trade]:
        """Submit a market order. Returns the trades it generated.

        A market order has no limit price, so it walks the opposite side from the best
        price outward until it is filled or the book runs dry. It **never rests** — any
        unfilled remainder is simply discarded, and the caller can detect this by checking
        `order.quantity` afterwards.

        The walk is the whole point of this project: how far it has to go before it fills
        is exactly the price impact being measured.
        """
        raise NotImplementedError

    def cancel(self, order_id: int) -> bool:
        """Remove a resting order. Returns True if it was found and removed.

        Returns False for an unknown id, or one that has already fully filled — cancelling
        something that no longer exists is a normal event in a real market, not an error.

        Remember to delete the price level if its queue becomes empty, or `best_bid` will
        start returning prices with nothing behind them.
        """
        raise NotImplementedError

    # ------------------------------------------------------------------ internals

    def _next_timestamp(self) -> int:
        self._clock += 1
        return self._clock

    def _assert_not_crossed(self) -> None:
        """The invariant. Leave this call in place after every mutation."""
        bid, ask = self.best_bid(), self.best_ask()
        if bid is not None and ask is not None and bid >= ask:
            raise AssertionError(f"book is crossed: best_bid={bid} >= best_ask={ask}")

    def _log(self, event: str, **fields) -> None:
        self.event_log.append({"seq": self._next_timestamp(), "event": event, **fields})

    def __repr__(self) -> str:
        try:
            bid, ask = self.best_bid(), self.best_ask()
        except NotImplementedError:
            return "<OrderBook (unimplemented)>"
        return f"<OrderBook bid={bid} ask={ask} trades={len(self.trades)}>"
