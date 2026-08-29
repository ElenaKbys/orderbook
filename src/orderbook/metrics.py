"""The measurement. This is the project; the engine is scaffolding for it.

NOT STARTED. Pick ONE of the two below and implement it properly rather than doing both
badly. Decide before you look at any results, and write the choice in NOTES.md.

A. Price impact
---------------
For a range of market-order sizes Q, measure how far the mid moves:

    impact(Q) = mid_after(Q) - mid_before

Repeat many times from a steady-state book, average by Q, and fit

    impact(Q) ~ k * Q**alpha

The claim under test is that alpha comes out meaningfully below 1 — concave impact, often
reported near 0.5. Report alpha with a confidence interval. If it comes out at 1, that is a
real result too: it says the concavity in real markets comes from something this model omits.

Watch for: measuring against a book that has not re-filled after the previous trade
(reset or wait between measurements), and averaging impact across different book states
without controlling for depth.

B. Market-maker P&L
-------------------
Run a naive market maker quoting a fixed spread around the mid. Decompose:

    P&L = spread capture - adverse selection

Spread capture is what it earns when it buys at bid and sells at ask. Adverse selection is
what it loses because trades arrive disproportionately just before the price moves against
it. Find the spread at which the two balance.

Watch for: forgetting inventory. A maker that accumulates a large one-sided position is
taking directional risk, not making markets, and its P&L will be dominated by luck.
"""

from __future__ import annotations


def price_impact_curve(book_factory, sizes, n_trials: int, seed: int = 0):
    """Measurement A. Returns (sizes, mean_impact, stderr). TO IMPLEMENT."""
    raise NotImplementedError


def fit_impact_exponent(sizes, impacts):
    """Fit impact ~ k * Q**alpha; return (alpha, stderr). TO IMPLEMENT.

    Fit in logs: log(impact) = log(k) + alpha * log(Q), then OLS. Drop non-positive
    impacts before taking logs rather than silently letting them become NaN.
    """
    raise NotImplementedError


def market_maker_pnl(book_factory, spread: int, n_steps: int, seed: int = 0):
    """Measurement B. Returns a dict with capture, adverse selection, inventory. TO IMPLEMENT."""
    raise NotImplementedError
