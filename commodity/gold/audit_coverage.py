"""Read-only price/NAV exact-date coverage audit for the five gold funds."""
import argparse
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent / "data/raw/funds"
FUNDS = ("ayar", "tala", "kahroba", "ganj", "gohar")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--start", default="2024-09-28")
    parser.add_argument("--end", default="2026-09-28")
    args = parser.parse_args()
    for fund in FUNDS:
        prices = pd.read_csv(ROOT / fund / "price.csv")
        traded = prices.loc[
            prices.date.between(args.start, args.end)
            & (prices.trade_volume > 0)
            & (prices.trade_count > 0)
        ]
        path = ROOT / fund / "nav_fipiran.csv"
        nav = pd.read_csv(path) if path.exists() else pd.DataFrame(columns=["date"])
        nav = nav.loc[nav.date.between(args.start, args.end)]
        missing = set(traded.date) - set(nav.date)
        print(f"{fund}: traded={len(traded)}, price_max={traded.date.max()}, "
              f"nav={len(nav)}, nav_max={nav.date.max() if len(nav) else '-'}, "
              f"matched={len(traded) - len(missing)}, missing={len(missing)}")


if __name__ == "__main__":
    main()
