"""Zero-intelligence order flow.

NOT STARTED. Implement after the matching engine passes its tests.

The model (Smith, Farmer, Gillemot & Krishnamurthy, 2003) has three independent Poisson
processes and no strategy whatsoever:

    limit orders   arrive at rate  lambda  per unit time, at a price drawn from some
                   distribution around the current mid
    market orders  arrive at rate  mu
    cancellations  each resting order is cancelled at rate  delta

That is the entire model. It is deliberately the dumbest defensible thing: nobody in it
knows anything, nobody reacts to anything. Which is the point — any structure that shows up
in the price-impact curve cannot have been smuggled in through trader behaviour, because
there is no behaviour. It has to be the mechanism.

Implementation notes
--------------------
* Seed the RNG and store the seed. Every figure must be reproducible.
* Simulate in event time, not wall-clock: draw the next event type with probability
  proportional to its rate, then draw its parameters.
* Run a burn-in before measuring anything, so the book reaches steady state. Choose the
  burn-in length by plotting depth against time and seeing where it flattens — do not
  guess a number and hope.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class FlowParams:
    """Rates for the three processes, plus the price distribution's width.

    Sensible starting values are not obvious and calibration is part of the work.
    Start with mu well below lambda, or the book empties and never refills.
    """

    limit_rate: float = 1.0
    market_rate: float = 0.2
    cancel_rate: float = 0.05
    tick_spread: int = 5
    seed: int = 0


class ZeroIntelligenceFlow:
    """Generates the order stream. TO IMPLEMENT."""

    def __init__(self, params: FlowParams) -> None:
        self.params = params
        raise NotImplementedError

    def next_event(self, book):
        """Draw and return the next order or cancellation."""
        raise NotImplementedError
