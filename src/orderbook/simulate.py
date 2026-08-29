"""Simulation loop: wires the flow model into the book. NOT STARTED."""

from __future__ import annotations

from .book import OrderBook
from .flow import FlowParams, ZeroIntelligenceFlow


def run(params: FlowParams, n_events: int, burn_in: int = 10_000) -> OrderBook:
    """Run the flow model against a fresh book and return it. TO IMPLEMENT.

    Discard the first `burn_in` events — the book starts empty, which is not a state any
    real market is ever in, and measuring during the fill-up phase produces nonsense.
    """
    raise NotImplementedError
