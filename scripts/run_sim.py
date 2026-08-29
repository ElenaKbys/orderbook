"""Entry point. Does nothing useful yet — the engine is not implemented.

Once it is:  python scripts/run_sim.py
"""

from orderbook.flow import FlowParams
from orderbook.simulate import run


def main() -> None:
    params = FlowParams(seed=0)
    book = run(params, n_events=100_000)
    print(book)


if __name__ == "__main__":
    main()
