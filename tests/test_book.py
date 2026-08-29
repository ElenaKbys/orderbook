"""Specification for the matching engine, written before the engine.

Every test below is a scenario worked out on paper — a book state where the correct answer
is known by hand. They are marked `xfail` because the implementation does not exist yet;
remove the marker from a test as soon as its behaviour is implemented, and the suite becomes
the progress bar.

Run with:  pytest -q
"""

import pytest

from orderbook.book import OrderBook
from orderbook.orders import Order, OrderType, Side

pytestmark = pytest.mark.xfail(
    reason="matching engine not implemented yet — see README roadmap",
    strict=False,
    raises=NotImplementedError,
)


def limit(side, price, qty, ts=0):
    return Order(side=side, price=price, quantity=qty, order_type=OrderType.LIMIT, timestamp=ts)


def market(side, qty, ts=0):
    return Order(side=side, quantity=qty, order_type=OrderType.MARKET, timestamp=ts)


# --------------------------------------------------------------------- empty book

def test_empty_book_has_no_prices():
    book = OrderBook()
    assert book.best_bid() is None
    assert book.best_ask() is None
    assert book.spread() is None
    assert book.mid() is None


# --------------------------------------------------------------------- resting

def test_single_bid_rests_and_becomes_best_bid():
    book = OrderBook()
    trades = book.add_limit_order(limit(Side.BUY, price=100, qty=10))
    assert trades == []
    assert book.best_bid() == 100
    assert book.best_ask() is None
    assert book.depth_at(Side.BUY, 100) == 10


def test_higher_bid_takes_priority():
    """Best bid is the *highest* buy price; best ask the *lowest* sell price."""
    book = OrderBook()
    book.add_limit_order(limit(Side.BUY, 100, 10))
    book.add_limit_order(limit(Side.BUY, 102, 5))
    book.add_limit_order(limit(Side.SELL, 110, 7))
    book.add_limit_order(limit(Side.SELL, 108, 3))
    assert book.best_bid() == 102
    assert book.best_ask() == 108
    assert book.spread() == 6
    assert book.mid() == 105.0


def test_depth_accumulates_at_a_level():
    book = OrderBook()
    book.add_limit_order(limit(Side.BUY, 100, 10))
    book.add_limit_order(limit(Side.BUY, 100, 15))
    assert book.depth_at(Side.BUY, 100) == 25


# --------------------------------------------------------------------- matching

def test_crossing_limit_order_trades_at_resting_price():
    """A buy at 105 hitting a resting ask at 100 trades at 100, not 105.

    The resting order set the terms. This is the convention that makes a market maker's
    spread capture positive, so getting it backwards quietly inverts the whole P&L study.
    """
    book = OrderBook()
    book.add_limit_order(limit(Side.SELL, 100, 10))
    trades = book.add_limit_order(limit(Side.BUY, 105, 10))
    assert len(trades) == 1
    assert trades[0].price == 100
    assert trades[0].quantity == 10
    assert book.best_ask() is None


def test_partial_fill_leaves_remainder_resting():
    """Buy 10 against 4 resting: 4 trade, 6 rest as the new best bid."""
    book = OrderBook()
    book.add_limit_order(limit(Side.SELL, 100, 4))
    trades = book.add_limit_order(limit(Side.BUY, 100, 10))
    assert sum(t.quantity for t in trades) == 4
    assert book.best_ask() is None
    assert book.best_bid() == 100
    assert book.depth_at(Side.BUY, 100) == 6


def test_price_priority_best_level_fills_first():
    """Asks at 100 and 101; a buy for 5 must take the 100 first."""
    book = OrderBook()
    book.add_limit_order(limit(Side.SELL, 101, 10))
    book.add_limit_order(limit(Side.SELL, 100, 3))
    trades = book.add_limit_order(limit(Side.BUY, 101, 5))
    assert [t.price for t in trades] == [100, 101]
    assert [t.quantity for t in trades] == [3, 2]
    assert book.depth_at(Side.SELL, 101) == 8


def test_time_priority_within_a_level():
    """Two asks at the same price: the earlier one fills first."""
    book = OrderBook()
    first = limit(Side.SELL, 100, 5, ts=1)
    second = limit(Side.SELL, 100, 5, ts=2)
    book.add_limit_order(first)
    book.add_limit_order(second)
    trades = book.add_limit_order(limit(Side.BUY, 100, 5, ts=3))
    assert len(trades) == 1
    assert trades[0].resting_order_id == first.order_id
    assert book.depth_at(Side.SELL, 100) == 5


def test_non_crossing_order_does_not_trade():
    book = OrderBook()
    book.add_limit_order(limit(Side.SELL, 110, 10))
    trades = book.add_limit_order(limit(Side.BUY, 100, 10))
    assert trades == []
    assert book.best_bid() == 100
    assert book.best_ask() == 110


# --------------------------------------------------------------------- market orders

def test_market_order_walks_the_book():
    """This is the price-impact mechanism in miniature."""
    book = OrderBook()
    book.add_limit_order(limit(Side.SELL, 100, 2))
    book.add_limit_order(limit(Side.SELL, 101, 2))
    book.add_limit_order(limit(Side.SELL, 103, 2))
    trades = book.add_market_order(market(Side.BUY, 5))
    assert [t.price for t in trades] == [100, 101, 103]
    assert [t.quantity for t in trades] == [2, 2, 1]
    assert book.best_ask() == 103
    assert book.depth_at(Side.SELL, 103) == 1


def test_market_order_never_rests():
    """With only 3 available, a market buy for 10 fills 3 and discards the rest."""
    book = OrderBook()
    book.add_limit_order(limit(Side.SELL, 100, 3))
    order = market(Side.BUY, 10)
    trades = book.add_market_order(order)
    assert sum(t.quantity for t in trades) == 3
    assert order.quantity == 7          # remainder is visible on the order
    assert book.best_bid() is None      # but it did NOT rest
    assert book.best_ask() is None


def test_market_order_into_empty_book_does_nothing():
    book = OrderBook()
    trades = book.add_market_order(market(Side.BUY, 10))
    assert trades == []


# --------------------------------------------------------------------- cancels

def test_cancel_removes_resting_order():
    book = OrderBook()
    order = limit(Side.BUY, 100, 10)
    book.add_limit_order(order)
    assert book.cancel(order.order_id) is True
    assert book.best_bid() is None
    assert book.depth_at(Side.BUY, 100) == 0


def test_cancel_unknown_id_returns_false():
    """Not an error — cancelling something already gone is normal in a live market."""
    book = OrderBook()
    assert book.cancel(999_999) is False


def test_cancel_one_of_two_at_a_level_leaves_the_other():
    book = OrderBook()
    a = limit(Side.BUY, 100, 5, ts=1)
    b = limit(Side.BUY, 100, 7, ts=2)
    book.add_limit_order(a)
    book.add_limit_order(b)
    book.cancel(a.order_id)
    assert book.depth_at(Side.BUY, 100) == 7
    assert book.best_bid() == 100


# --------------------------------------------------------------------- the invariant

def test_book_is_never_crossed():
    """If this ever fails, stop and fix it before doing anything else."""
    book = OrderBook()
    book.add_limit_order(limit(Side.SELL, 100, 5))
    book.add_limit_order(limit(Side.BUY, 105, 5))   # must trade, not rest above the ask
    bid, ask = book.best_bid(), book.best_ask()
    assert bid is None or ask is None or bid < ask
