"""Build explicit two-year daily price/NAV tables without filling NAV gaps."""
import argparse
import sys
from datetime import date
from pathlib import Path

import pandas as pd

PROJECT = Path(__file__).resolve().parent
ROOT = PROJECT.parents[1]
sys.path.insert(0, str(ROOT))
from shared.market_analysis.bubble_distribution import _atomic_csv

FUNDS = ("ayar", "tala", "kahroba", "ganj", "gohar")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--as-of", default=date.today().isoformat(),
                        help="Inclusive end date, YYYY-MM-DD")
    args = parser.parse_args()
    end = pd.Timestamp(args.as_of)
    start = end - pd.DateOffset(years=2)
    output = PROJECT / "data/processed/analysis"
    for fund in FUNDS:
        raw = PROJECT / "data/raw/funds" / fund
        prices = pd.read_csv(raw / "price.csv", parse_dates=["date"])
        prices = prices.loc[
            prices.date.between(start, end)
            & (prices.trade_volume > 0)
            & (prices.trade_count > 0),
            ["date", "closing_price_irr", "trade_volume", "trade_count", "source_snapshot"],
        ].rename(columns={"source_snapshot": "price_source_snapshot"})
        nav_path = raw / "nav_fipiran.csv"
        nav_provider = "fipiran_historical"
        if fund == "ayar" and not nav_path.exists():
            raise FileNotFoundError(f"Ayar Fipiran NAV not collected: {nav_path}")
        if fund != "ayar" and not nav_path.exists():
            nav_path = raw / "nav.csv"
            nav_provider = "tsetmc_historical"
        if nav_path.exists():
            nav = pd.read_csv(nav_path, parse_dates=["date"])
            nav = nav.loc[nav.date.between(start, end),
                          ["date", "redemption_nav_irr", "source_snapshot"]]
            nav = nav.rename(columns={"source_snapshot": "nav_source_snapshot"})
            result = prices.merge(nav, on="date", how="left", validate="one_to_one")
            result["nav_provider"] = nav_provider
        else:
            result = prices.copy()
            result["redemption_nav_irr"] = pd.NA
            result["nav_source_snapshot"] = pd.NA
            result["nav_provider"] = pd.NA
        result.insert(1, "fund", fund)
        result["nav_available"] = result.redemption_nav_irr.notna()
        result["date"] = result.date.dt.strftime("%Y-%m-%d")
        path = output / f"{fund}_daily_price_nav_2y.csv"
        _atomic_csv(result.sort_values("date"), path)
        print(f"{fund}: {len(result)} traded dates; "
              f"{int(result.nav_available.sum())} exact-date NAV matches; {path}")


if __name__ == "__main__":
    main()
