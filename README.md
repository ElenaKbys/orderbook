# Limit Order Book Simulator

A price–time-priority matching engine, driven by a stochastic order-flow model, used to
measure **how far the price moves when you trade** — and whether that relationship comes out
concave, as the empirical market-microstructure literature reports.

> **Status: in progress.** Started September 2026. The repository is scaffolded and the test
> suite is written; the engine is being implemented against it. See the [roadmap](#roadmap)
> for exactly what does and does not work today. Nothing in this README describes a result I
> have measured yet.

---

## The question

A limit order book is the data structure an exchange actually uses: resting buy and sell
orders, matched by price first and then by arrival time. Building one is a well-trodden
exercise. **Building one is not the point of this project.**

The point is the measurement on top of it. If you buy 1,000 shares, the price moves against
you — you consume the best offers and walk up the book. The interesting empirical claim is
that this relationship is *concave*: doubling your trade size does **not** double your cost.
Price impact grows roughly like the square root of volume, a regularity reported across many
markets and asset classes.

**This project asks whether that shape emerges from a book driven by order flow with no
intelligence in it at all** — no informed traders, no strategy, just random arrivals. If it
does, the shape is a property of the mechanism rather than of trader behaviour. That is a
result worth having, and it is the reason the engine exists.

## Design decisions

**Price–time priority.** Orders match by best price first; ties broken by arrival time. This
is the rule used by most equity exchanges, and it means the book is a pair of price-indexed
queues rather than a flat list.

**Zero-intelligence order flow.** Order arrivals, cancellations and market orders are drawn
from independent Poisson processes with fixed rates. This is deliberately the dumbest
defensible model. It makes no claim about how real traders behave, which is exactly why any
structure that emerges from it is attributable to the *mechanism* and not to assumptions I
smuggled in.

**Discrete price grid.** Prices live on integer ticks. Real books do too, and it avoids a
class of floating-point equality bugs.

**Event log over snapshots.** Every order, cancellation and trade is appended to a log. All
analysis is derived from the log rather than from book snapshots, so any measurement can be
recomputed without re-running the simulation.

## What gets measured

Two candidate results. **One will be chosen; both are specified so the choice is deliberate
rather than accidental.**

**A · Price impact curve.** Submit market orders of varying size against a book in steady
state. Measure mid-price displacement against executed volume. Fit and report the exponent —
the claim under test is that it lands meaningfully below 1 (concave), near 0.5.

**B · Market-maker P&L decomposition.** Run a naive fixed-spread market maker inside the
simulation and split its P&L into spread capture minus adverse selection, then find the spread
at which it breaks even.

Whichever is chosen, the deliverable is a plot plus an honest statement of what it shows —
**including if it shows nothing.** A clean null with a correct method is a real result.

## Repository layout

```
orderbook/
├── src/orderbook/
│   ├── orders.py      Order, Trade, Side, OrderType   [implemented]
│   ├── book.py        matching engine                 [in progress]
│   ├── flow.py        zero-intelligence order flow    [not started]
│   ├── metrics.py     impact / P&L decomposition      [not started]
│   └── simulate.py    simulation loop                 [not started]
├── tests/
│   ├── test_orders.py   passing
│   └── test_book.py     the specification — see note below
├── scripts/run_sim.py
├── figures/
└── NOTES.md           running log of decisions and things that confused me
```

## The test suite is the specification

`tests/test_book.py` was written **before** the engine, and each test encodes a scenario
worked out by hand on paper — a case where I already know what the book should look like
afterwards. Unimplemented behaviour is marked `xfail`, so the suite runs green and reports
honestly what is outstanding:

```
pytest -q
# ... x = expected failure, i.e. specified but not yet implemented
```

As each method is implemented, its `xfail` marker comes off. The count of remaining `xfail`s
is the progress bar.

## Running it

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
pytest -q
```

The simulation entry point is `scripts/run_sim.py`. It does not produce output yet.

## Roadmap

- [x] Repository scaffold, dependencies, test harness
- [x] Order and trade types
- [x] Test suite written as the specification
- [ ] Matching engine: limit orders, resting book, price–time priority
- [ ] Market orders, partial fills, walking the book
- [ ] Cancellations
- [ ] Event log
- [ ] Zero-intelligence flow model
- [ ] Steady-state calibration and burn-in
- [ ] Measurement A or B, chosen and implemented
- [ ] Figures and results write-up

## Scope, honestly

This is a two-week project built alongside coursework. It is a **toy**: single asset, no
fees, no latency, no queue-position modelling, no informed traders, no hidden liquidity.
Any number it produces is a statement about the model, not about a real market. I would
rather say that plainly here than have it inferred later.

## References

- Gould et al. (2013), *Limit Order Books* — the survey; start here.
- Smith, Farmer, Gillemot & Krishnamurthy (2003), *Statistical theory of the continuous
  double auction* — the zero-intelligence model this follows.
- Bouchaud, Farmer & Lillo (2009), *How Markets Slowly Digest Changes in Supply and Demand* —
  the price-impact literature, including the square-root law.

---

*Elena Kobayashi · UCLA Mathematics · [github](https://github.com/) · [linkedin](https://linkedin.com/)*
