"""Frequency-matched, dividend-reinvested REIT correlation grids."""

from __future__ import annotations

from datetime import date, timedelta
from math import ceil
from pathlib import Path

import numpy as np
import pandas as pd

from asset_allocation.analyze_reit_tedpix_weekly import atomic_frame, latest_complete_friday, shift_jalali_months
from asset_allocation.build_reit_reinvested_correlations import (
    TEDPIX, USD, WEEKLY_RETURNS, MONTHLY_RETURNS, month, previous_month, returns,
)
from asset_allocation.build_reit_assembly_reinvestment import OUTPUT as REITS
from asset_allocation.analyze_reit_housing_monthly import HOUSING

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "data/processed/analysis/reit_requested_correlation_heatmaps.csv"
FUNDS = ("Arzesh Maskan", "Kelid", "Danik", "Kakh")
WINDOWS = {"daily": (1, 3, 6, 12), "weekly": (1, 3, 6, 12, 24),
           "monthly": (12, 24, 36)}
USD_LAGS = {1: 4, 3: 13, 6: 26}  # Completed Friday-ending weeks.
MIN_PAIRS = 5


def daily_returns(frame: pd.DataFrame, *, usd: bool = False) -> pd.DataFrame:
    """Return between adjacent observed sessions; do not bridge long trading gaps."""
    data = frame.sort_values("date").copy()
    if data.date.duplicated().any() or (data.level <= 0).any():
        raise ValueError("Duplicate date or nonpositive level")
    gap = data.date.diff().dt.days
    eligible = gap.le(5)
    if usd:
        eligible &= data.price_method.eq(data.price_method.shift())
    data["return"] = (data.level / data.level.shift() - 1).where(eligible)
    data["period"] = data.date.dt.strftime("%Y-%m-%d")
    return data[["period", "return"]]


def correlation_rows(reits: pd.DataFrame, benchmark: pd.DataFrame, *, name: str,
                     frequency: str, anchor: date, windows: tuple[int, ...]) -> list[dict]:
    if benchmark.period.duplicated().any():
        raise ValueError(f"Duplicate {name}/{frequency} period")
    output = []
    for fund in FUNDS:
        own = reits.loc[reits.fund.eq(fund), ["period", "reinvested_return"]]
        if own.period.duplicated().any():
            raise ValueError(f"Duplicate {fund}/{frequency} period")
        paired = own.merge(benchmark, on="period", how="inner", validate="one_to_one")
        for window in windows:
            if frequency == "monthly":
                end = previous_month(month(anchor))
                periods = [end]
                for _ in range(window - 1):
                    periods.append(previous_month(periods[-1]))
                sample = paired.loc[paired.period.isin(periods)]
                start = periods[-1]
            else:
                start = shift_jalali_months(anchor, window).isoformat()
                sample = paired.loc[(paired.period > start) & (paired.period <= anchor.isoformat())]
            sample = sample.dropna(subset=["reinvested_return", "return"])
            n = len(sample)
            expected = window if frequency == "monthly" else window * (52 / 12 if frequency == "weekly" else 20)
            required = max(MIN_PAIRS, ceil(expected * 0.7))
            valid = n >= required and sample.reinvested_return.nunique() > 1 and sample["return"].nunique() > 1
            output.append({"benchmark": name, "frequency": frequency, "fund": fund,
                           "window_months": window, "lag_months": 0, "lag_weeks": 0,
                           "window_start": start, "window_end": end if frequency == "monthly" else anchor.isoformat(),
                           "paired_observations": n, "minimum_pairs": required,
                           "correlation": sample.reinvested_return.corr(sample["return"]) if valid else np.nan,
                           "status": "reported" if valid else "insufficient_pairs_or_variation"})
    return output


def dollar_lag_rows(reits: pd.DataFrame, usd: pd.DataFrame, anchor: date) -> list[dict]:
    """USD leads the REIT by 4/13/26 complete calendar weeks in one 24-month sample."""
    start = shift_jalali_months(anchor, 24)
    first = start - timedelta(weeks=max(USD_LAGS.values()) + 2)
    weeks = pd.date_range(first, anchor, freq="W-FRI").strftime("%Y-%m-%d")
    panel = pd.DataFrame(index=pd.Index(weeks, name="period"))
    if usd.period.duplicated().any():
        raise ValueError("Duplicate USD week")
    panel["usd"] = usd.set_index("period")["return"].reindex(panel.index)
    for fund in FUNDS:
        own = reits.loc[reits.fund.eq(fund)]
        if own.period.duplicated().any():
            raise ValueError(f"Duplicate {fund} week")
        panel[fund] = own.set_index("period").reinvested_return.reindex(panel.index)
    panel = panel.loc[(panel.index > start.isoformat()) & (panel.index <= anchor.isoformat())].copy()
    rows = []
    full_usd = usd.set_index("period")["return"].reindex(weeks)
    for lag_months, lag_weeks in USD_LAGS.items():
        panel["lagged_usd"] = full_usd.shift(lag_weeks).reindex(panel.index)
        for fund in FUNDS:
            sample = panel[[fund, "lagged_usd"]].dropna()
            n = len(sample)
            required = max(MIN_PAIRS, ceil(105 * 0.7))
            valid = n >= required and sample[fund].nunique() > 1 and sample.lagged_usd.nunique() > 1
            rows.append({"benchmark": "USD/IRR leads REIT", "frequency": "weekly",
                         "fund": fund, "window_months": 24, "lag_months": lag_months,
                         "lag_weeks": lag_weeks, "window_start": start.isoformat(),
                         "window_end": anchor.isoformat(), "paired_observations": n,
                         "minimum_pairs": required,
                         "correlation": sample[fund].corr(sample.lagged_usd) if valid else np.nan,
                         "status": "reported" if valid else "insufficient_pairs_or_variation"})
    return rows


def build(anchor: date | None = None) -> pd.DataFrame:
    anchor = anchor or latest_complete_friday()
    reits = pd.read_csv(REITS, dtype={"ins_code": str})
    reits["date"] = pd.to_datetime(reits.source_date_gregorian)
    reits["level"] = pd.to_numeric(reits.reinvested_value_irr)
    index = pd.read_csv(TEDPIX)
    index["date"] = pd.to_datetime(index.source_date_gregorian)
    index["level"] = pd.to_numeric(index.index_close)
    fx = pd.read_csv(USD)
    fx["date"] = pd.to_datetime(fx.date_gr.str.replace("/", "-", regex=False))
    fx["level"] = pd.to_numeric(fx.price_irr.str.replace(",", "", regex=False))
    rows = []
    for frequency in WINDOWS:
        if frequency == "daily":
            own = pd.concat([daily_returns(group).assign(fund=fund).rename(columns={"return": "reinvested_return"})
                             for fund, group in reits.groupby("fund")], ignore_index=True)
            benchmarks = {"TEDPIX": daily_returns(index), "USD/IRR": daily_returns(fx, usd=True)}
        else:
            own = pd.read_csv(WEEKLY_RETURNS if frequency == "weekly" else MONTHLY_RETURNS)
            benchmarks = {"TEDPIX": returns(index.assign(date=index.date.dt.date), frequency, anchor)}
            if frequency == "weekly":
                benchmarks["USD/IRR"] = returns(fx.assign(date=fx.date.dt.date), frequency, anchor, usd=True)
        for name, benchmark in benchmarks.items():
            if name == "USD/IRR" and frequency == "weekly":
                continue
            windows = (1, 3) if name == "USD/IRR" and frequency == "daily" else WINDOWS[frequency]
            rows.extend(correlation_rows(own, benchmark, name=name, frequency=frequency,
                                         anchor=anchor, windows=windows))
        if frequency == "weekly":
            rows.extend(dollar_lag_rows(own, benchmarks["USD/IRR"], anchor))
        if frequency == "monthly":
            housing = pd.read_csv(HOUSING, dtype={"jalali_period": str})
            housing = housing.loc[housing.asset_id.eq("tehran_housing"),
                                  ["jalali_period", "monthly_return"]].rename(
                                      columns={"jalali_period": "period", "monthly_return": "return"})
            rows.extend(correlation_rows(own, housing, name="Tehran housing", frequency="monthly",
                                         anchor=anchor, windows=WINDOWS["monthly"]))
    result = pd.DataFrame(rows)
    atomic_frame(OUTPUT, result)
    return result


if __name__ == "__main__":
    result = build()
    print(f"Wrote {len(result)} cells; {result.correlation.notna().sum()} reportable")
