"""Normalize weekly REIT, USD/IRR, and TEDPIX levels over the last two years."""

from __future__ import annotations

import csv
from datetime import date, timedelta
from pathlib import Path

import pandas as pd

from asset_allocation.analyze_reit_tedpix_weekly import (
    ENGLISH_NAMES, INDEX, MANIFEST, atomic_frame, friday,
    latest_complete_friday, shift_jalali_months, weekly_closes,
)
from asset_allocation.analyze_reit_usd_weekly import USD_RAW, usd_weekly_closes
from asset_allocation.build_reit_assembly_reinvestment import OUTPUT as REINVESTED, FUNDS

OUTPUT_DIR = Path(__file__).resolve().parents[2] / "data/processed/analysis"
PANEL = OUTPUT_DIR / "reit_usd_tedpix_two_year_cumulative.csv"
SUMMARY = OUTPUT_DIR / "reit_usd_tedpix_two_year_cumulative_summary.csv"


def reinvested_weekly_closes(path: Path, code: str, cutoff: date, anchor: date) -> dict[date, tuple]:
    closes = {}
    seen = set()
    with path.open(encoding="utf-8", newline="") as source:
        for row in csv.DictReader(source):
            if row["ins_code"] != code:
                continue
            observed = date.fromisoformat(row["source_date_gregorian"])
            if observed < cutoff or observed > anchor:
                continue
            if observed in seen:
                raise ValueError(f"Duplicate adjusted close for {code} on {observed}")
            seen.add(observed)
            price = float(row["reinvested_value_irr"])
            if price <= 0:
                raise ValueError(f"Invalid reinvested value for {code} on {observed}")
            week = friday(observed)
            if week <= anchor and (week not in closes or observed.isoformat() > closes[week][1]):
                closes[week] = (price, observed.isoformat(), "assembly_date_reinvested_traded_close")
    return closes


def build(anchor: date | None = None) -> tuple[pd.DataFrame, pd.DataFrame]:
    anchor = anchor or latest_complete_friday()
    cutoff = shift_jalali_months(anchor, 24)
    with MANIFEST.open(encoding="utf-8", newline="") as source:
        funds = list(csv.DictReader(source))
    index = weekly_closes(INDEX, "index_close", cutoff, anchor)
    usd = usd_weekly_closes(USD_RAW, cutoff, anchor)
    series = [("TEDPIX", "index_level", {week: (float(row["index_close"]), row["source_date_gregorian"], "TSETMC_index")
                                           for week, row in index.items()}),
              ("USD/IRR", "IRR_per_USD", {week: (row["price"], row["observed"].isoformat(), row["method"])
                                           for week, row in usd.items()})]
    for fund in funds:
        code = fund["ins_code"]
        if code not in FUNDS:
            continue
        if code not in ENGLISH_NAMES:
            raise ValueError(f"English fund name required for {code}")
        closes = reinvested_weekly_closes(REINVESTED, code, cutoff, anchor)
        series.append((ENGLISH_NAMES[code], "IRR_per_fund_unit",
                       closes))
    weeks = []
    week = friday(cutoff)
    while week <= anchor:
        weeks.append(week)
        week += timedelta(days=7)
    rows, summaries = [], []
    for asset, unit, closes in series:
        available = [week for week in weeks if week in closes]
        if not available:
            raise ValueError(f"No weekly observations for {asset}")
        baseline_week = available[0]
        baseline_level = closes[baseline_week][0]
        last_week = available[-1]
        for week in weeks:
            close = closes.get(week)
            rows.append({"week_end_gregorian": week.isoformat(), "asset": asset, "unit": unit,
                         "source_observation_date": close[1] if close else "",
                         "weekly_level": close[0] if close else float("nan"),
                         "price_method": close[2] if close else "",
                         "baseline_week_end": baseline_week.isoformat(),
                         "baseline_level": baseline_level,
                         "return_definition": "assembly_date_cash_reinvested_traded_close_scenario" if asset not in ("TEDPIX", "USD/IRR") else
                         ("index_level_change" if asset == "TEDPIX" else "usd_irr_level_change"),
                         "cumulative_return": close[0] / baseline_level - 1 if close else float("nan")})
        summaries.append({"asset": asset, "baseline_week_end": baseline_week.isoformat(),
                          "latest_observed_week_end": last_week.isoformat(),
                          "baseline_level": baseline_level, "latest_level": closes[last_week][0],
                          "cumulative_return": closes[last_week][0] / baseline_level - 1,
                          "observed_weeks": len(available)})
    panel, summary = pd.DataFrame(rows), pd.DataFrame(summaries)
    atomic_frame(PANEL, panel)
    atomic_frame(SUMMARY, summary)
    return panel, summary


if __name__ == "__main__":
    panel, summary = build()
    print(f"Wrote {len(panel)} weekly asset rows and {len(summary)} asset summaries through {panel.week_end_gregorian.max()}")
