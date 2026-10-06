"""Normalize observed monthly Tehran housing levels within the two-year chart window."""

from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path

import jdatetime
import pandas as pd

from asset_allocation.analyze_reit_tedpix_weekly import atomic_frame, latest_complete_friday, shift_jalali_months

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "data/processed/analysis/monthly_asset_levels.csv"
PANEL = ROOT / "data/processed/analysis/tehran_housing_two_year_cumulative.csv"
SUMMARY = ROOT / "data/processed/analysis/tehran_housing_two_year_cumulative_summary.csv"


def gregorian_month_end(period: str) -> date:
    year, month = map(int, period.split("/"))
    next_year, next_month = (year + 1, 1) if month == 12 else (year, month + 1)
    return jdatetime.date(next_year, next_month, 1).togregorian() - timedelta(days=1)


def build(anchor: date | None = None, source: Path = SOURCE) -> tuple[pd.DataFrame, pd.DataFrame]:
    anchor = anchor or latest_complete_friday()
    cutoff = shift_jalali_months(anchor, 24)
    data = pd.read_csv(source, dtype={"jalali_period": str})
    housing = data.loc[data.asset_id == "tehran_housing"].copy()
    if housing.jalali_period.duplicated().any():
        raise ValueError("Duplicate Tehran housing month")
    housing["observation_date_gregorian"] = housing.jalali_period.map(gregorian_month_end)
    housing["month_end_level"] = pd.to_numeric(housing.month_end_level, errors="coerce")
    housing = housing.loc[(housing.observation_date_gregorian >= cutoff) &
                          (housing.observation_date_gregorian <= anchor) &
                          housing.month_end_level.notna()].sort_values("observation_date_gregorian")
    if housing.empty or (housing.month_end_level <= 0).any():
        raise ValueError("No valid positive Tehran housing levels in the two-year window")
    baseline = housing.iloc[0]
    housing["cumulative_return"] = housing.month_end_level / baseline.month_end_level - 1
    panel = housing[["jalali_period", "observation_date_gregorian", "month_end_level",
                     "source_method", "data_quality_flag", "cumulative_return"]].copy()
    panel.insert(0, "asset", "Tehran housing")
    panel["observation_date_gregorian"] = panel.observation_date_gregorian.map(date.isoformat)
    panel["baseline_observation_date"] = baseline.observation_date_gregorian.isoformat()
    panel["baseline_level"] = baseline.month_end_level
    summary = pd.DataFrame([{"asset": "Tehran housing", "frequency": "monthly",
                             "baseline_observation_date": baseline.observation_date_gregorian.isoformat(),
                             "latest_observation_date": housing.iloc[-1].observation_date_gregorian.isoformat(),
                             "baseline_level": baseline.month_end_level,
                             "latest_level": housing.iloc[-1].month_end_level,
                             "cumulative_return": housing.iloc[-1].cumulative_return,
                             "observed_months": len(housing),
                             "source_method": housing.iloc[-1].source_method,
                             "data_quality_flag": housing.iloc[-1].data_quality_flag}])
    atomic_frame(PANEL, panel)
    atomic_frame(SUMMARY, summary)
    return panel, summary


if __name__ == "__main__":
    panel, summary = build()
    print(f"Wrote {len(panel)} observed monthly Tehran housing points through {summary.latest_observation_date.iloc[0]}")
