"""Tests for the value types. These pass today."""

import pytest

from orderbook.orders import Order, OrderType, Side, Trade


def test_side_opposite():
    assert Side.BUY.opposite is Side.SELL
    assert Side.SELL.opposite is Side.BUY


def test_order_ids_are_unique():
    a = Order(side=Side.BUY, price=100, quantity=1)
    b = Order(side=Side.BUY, price=100, quantity=1)
    assert a.order_id != b.order_id


def test_limit_order_requires_a_price():
    with pytest.raises(ValueError, match="limit orders require a price"):
        Order(side=Side.BUY, quantity=10, order_type=OrderType.LIMIT)


def test_market_order_must_not_have_a_price():
    with pytest.raises(ValueError, match="must not carry a price"):
        Order(side=Side.BUY, quantity=10, price=100, order_type=OrderType.MARKET)


def test_quantity_must_be_positive():
    with pytest.raises(ValueError, match="quantity must be positive"):
        Order(side=Side.BUY, price=100, quantity=0)


def test_is_filled():
    order = Order(side=Side.BUY, price=100, quantity=5)
    assert not order.is_filled
    order.quantity = 0
    assert order.is_filled


def test_trade_notional():
    t = Trade(price=100, quantity=3, resting_order_id=1, incoming_order_id=2, timestamp=0)
    assert t.notional == 300
