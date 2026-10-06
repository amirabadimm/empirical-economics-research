"""Build monthly traded-price returns for real-estate funds and TEDPIX."""

from __future__ import annotations

import csv
import os
import tempfile
from datetime import date
from pathlib import Path

import jdatetime

from asset_allocation.build_monthly_return_panel import periods, previous_period
from asset_allocation.collectors.tsetmc_reits import MANIFEST, RAW

ROOT = Path(__file__).resolve().parents[2]
INDEX = ROOT / "data/raw/tse_total_index/tedpix_daily.csv"
OUTPUT = ROOT / "data/processed/analysis/reit_tedpix_monthly_returns.csv"
FIELDS = ("jalali_period", "asset_id", "ticker", "source_observation_date", "month_end_level",
          "previous_jalali_period", "previous_month_end_level", "monthly_return", "return_definition", "missing_reason")


def month(date_string: str) -> str:
    d = jdatetime.date.fromgregorian(date=date.fromisoformat(date_string))
    return f"{d.year:04}/{d.month:02}"


def month_ends(path: Path, field: str, traded_only: bool) -> dict[str, dict]:
    output = {}
    with path.open(encoding="utf-8", newline="") as file:
        for row in csv.DictReader(file):
            if traded_only and row["has_trade"] != "true":
                continue
            period = month(row["source_date_gregorian"])
            if period not in output or row["source_date_gregorian"] > output[period]["source_date_gregorian"]:
                output[period] = row
    return output


def build() -> dict[str, int]:
    with MANIFEST.open(encoding="utf-8", newline="") as file:
        funds = list(csv.DictReader(file))
    series = [("equity_tedpix", "شاخص کل", month_ends(INDEX, "index_close", False), "index_close", "index_level_change")]
    for fund in funds:
        code = fund["ins_code"]
        series.append((f"reit_{code}", fund["ticker"], month_ends(RAW / f"{code}.csv", "closing_price_irr", True),
                       "closing_price_irr", "traded_closing_price_change_distributions_unaudited"))
    last = max(max(levels) for _, _, levels, _, _ in series)
    first = min(min(levels) for _, _, levels, _, _ in series[1:])
    output = []
    for period in periods(first, last):
        prior = previous_period(period)
        for asset, ticker, levels, field, definition in series:
            current, previous = levels.get(period), levels.get(prior)
            current_level = current[field] if current else ""
            previous_level = previous[field] if previous else ""
            result = str(float(current_level) / float(previous_level) - 1) if current and previous else ""
            output.append({"jalali_period": period, "asset_id": asset, "ticker": ticker,
                           "source_observation_date": current["source_date_gregorian"] if current else "",
                           "month_end_level": current_level, "previous_jalali_period": prior,
                           "previous_month_end_level": previous_level, "monthly_return": result,
                           "return_definition": definition,
                           "missing_reason": "" if result else ("no_current_trade" if not current else "no_previous_month_trade")})
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", delete=False,
                                     dir=OUTPUT.parent, suffix=".tmp") as file:
        writer = csv.DictWriter(file, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(output)
        temporary = Path(file.name)
    os.replace(temporary, OUTPUT)
    return {"rows": len(output), "funds": len(funds), "first_period": first, "last_period": last}


if __name__ == "__main__":
    print(build())
