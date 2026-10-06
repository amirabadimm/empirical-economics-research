"""Same-period REIT correlations using assembly-date reinvested traded closes."""

from __future__ import annotations

from math import ceil
from datetime import date
from pathlib import Path

import jdatetime
import numpy as np
import pandas as pd

from asset_allocation.analyze_reit_tedpix_weekly import atomic_frame, friday, latest_complete_friday, shift_jalali_months
from asset_allocation.build_reit_assembly_reinvestment import OUTPUT as REITS

ROOT = Path(__file__).resolve().parents[2]
TEDPIX = ROOT / "data/raw/tse_total_index/tedpix_daily.csv"
USD = ROOT.parents[0] / "shared/data/raw/fx/usd_to_rial.csv"
OUTPUT = ROOT / "data/processed/analysis/reit_reinvested_correlations.csv"
WEEKLY_RETURNS = ROOT / "data/processed/analysis/reit_reinvested_weekly_returns.csv"
MONTHLY_RETURNS = ROOT / "data/processed/analysis/reit_reinvested_monthly_returns.csv"
WINDOWS = {"weekly": (3, 6, 12, 24), "monthly": (6, 12, 24, 48)}
MIN_PAIRS = {"weekly": 12, "monthly": 6}


def month(day: date) -> str:
    value = jdatetime.date.fromgregorian(date=day)
    return f"{value.year:04}/{value.month:02}"


def previous_month(period: str) -> str:
    year, m = map(int, period.split("/"))
    return f"{year-1:04}/12" if m == 1 else f"{year:04}/{m-1:02}"


def returns(frame: pd.DataFrame, frequency: str, anchor: date, usd: bool = False) -> pd.DataFrame:
    frame = frame.loc[frame.date <= anchor].sort_values("date").copy()
    if frame.date.duplicated().any() or (frame.level <= 0).any():
        raise ValueError("Duplicate date or nonpositive level")
    frame["period"] = frame.date.map(lambda d: friday(d).isoformat() if frequency == "weekly" else month(d))
    if frequency == "weekly":
        frame = frame.loc[frame.period <= anchor.isoformat()]
    else:
        frame = frame.loc[frame.period < month(anchor)]
    frame = frame.groupby("period", as_index=False).tail(1).sort_values("period").copy()
    frame["previous_period"] = frame.period.shift(1)
    frame["previous_level"] = frame.level.shift(1)
    if frequency == "weekly":
        adjacent = frame.apply(lambda r: pd.notna(r.previous_period) and
                               (date.fromisoformat(r.period) - date.fromisoformat(r.previous_period)).days == 7, axis=1)
    else:
        adjacent = frame.apply(lambda r: pd.notna(r.previous_period) and
                               previous_month(r.period) == r.previous_period, axis=1)
    if usd:
        adjacent &= frame.price_method.eq(frame.price_method.shift(1))
    frame["return"] = np.where(adjacent, frame.level / frame.previous_level - 1, np.nan)
    return frame[["period", "return"]]


def analyze(anchor: date | None = None) -> pd.DataFrame:
    anchor = anchor or latest_complete_friday()
    reits = pd.read_csv(REITS, dtype={"ins_code": str})
    reits["date"] = pd.to_datetime(reits.source_date_gregorian).dt.date
    reits["level"] = reits.reinvested_value_irr.astype(float)
    index = pd.read_csv(TEDPIX)
    index["date"] = pd.to_datetime(index.source_date_gregorian).dt.date
    index["level"] = pd.to_numeric(index.index_close)
    fx = pd.read_csv(USD)
    fx["date"] = pd.to_datetime(fx.date_gr.str.replace("/", "-", regex=False)).dt.date
    fx["level"] = pd.to_numeric(fx.price_irr.str.replace(",", "", regex=False))
    rows = []
    for frequency, windows in WINDOWS.items():
        benchmarks = {"TEDPIX": returns(index, frequency, anchor),
                      "USD/IRR": returns(fx, frequency, anchor, usd=True)}
        fund_returns = {fund: returns(group, frequency, anchor)
                        for fund, group in reits.groupby("fund")}
        for fund, own in fund_returns.items():
            for benchmark, other in benchmarks.items():
                paired = own.merge(other, on="period", how="inner", suffixes=("_reit", "_benchmark"))
                for window in windows:
                    if frequency == "weekly":
                        cutoff = shift_jalali_months(anchor, window).isoformat()
                        sample = paired.loc[(paired.period > cutoff) & (paired.period <= anchor.isoformat())]
                    else:
                        latest = previous_month(month(anchor))
                        periods = [latest]
                        for _ in range(window - 1):
                            periods.append(previous_month(periods[-1]))
                        sample = paired.loc[paired.period.isin(periods)]
                    sample = sample.dropna(subset=["return_reit", "return_benchmark"])
                    n = len(sample)
                    expected = window * (52 / 12 if frequency == "weekly" else 1)
                    required = max(MIN_PAIRS[frequency], ceil(expected * 0.7))
                    valid = n >= required and sample.return_reit.nunique() > 1 and sample.return_benchmark.nunique() > 1
                    rows.append({"fund": fund, "benchmark": benchmark, "frequency": frequency,
                                 "window_months": window, "paired_observations": n,
                                 "minimum_pairs": required,
                                 "correlation": sample.return_reit.corr(sample.return_benchmark) if valid else np.nan,
                                 "status": "reported" if valid else "insufficient_pairs_or_variation",
                                 "return_definition": "assembly_date_reinvested_traded_close_scenario"})
    return pd.DataFrame(rows)


def build(anchor: date | None = None) -> pd.DataFrame:
    anchor = anchor or latest_complete_friday()
    reits = pd.read_csv(REITS, dtype={"ins_code": str})
    reits["date"] = pd.to_datetime(reits.source_date_gregorian).dt.date
    reits["level"] = reits.reinvested_value_irr.astype(float)
    for frequency, target in (("weekly", WEEKLY_RETURNS), ("monthly", MONTHLY_RETURNS)):
        panels = []
        for fund, group in reits.groupby("fund"):
            table = returns(group, frequency, anchor).rename(columns={"return": "reinvested_return"})
            table.insert(0, "fund", fund)
            panels.append(table)
        atomic_frame(target, pd.concat(panels, ignore_index=True))
    result = analyze(anchor)
    atomic_frame(OUTPUT, result)
    return result


if __name__ == "__main__":
    result = build()
    print(f"Wrote {len(result)} cells; {result.correlation.notna().sum()} reportable")
