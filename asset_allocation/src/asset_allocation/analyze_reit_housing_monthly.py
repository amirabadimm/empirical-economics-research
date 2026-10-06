"""Same-Jalali-month REIT and Tehran housing return correlations; no lags."""

from __future__ import annotations

from math import ceil
from pathlib import Path

import numpy as np
import pandas as pd

from asset_allocation.analyze_reit_tedpix_weekly import atomic_frame
from asset_allocation.build_reit_reinvested_correlations import MONTHLY_RETURNS, previous_month

ROOT = Path(__file__).resolve().parents[2]
HOUSING = ROOT / "data/processed/analysis/monthly_asset_returns.csv"
PAIRS = ROOT / "data/processed/analysis/reit_housing_monthly_pairs.csv"
SUMMARY = ROOT / "data/processed/analysis/reit_housing_monthly_correlation.csv"
FUNDS = ("Arzesh Maskan", "Kelid", "Danik", "Kakh")


def analyze(housing: pd.DataFrame, reits: pd.DataFrame, *, months: int = 24,
            min_pairs: int = 12, min_coverage: float = 0.7) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Align observed returns by exact Jalali month and suppress thin samples."""
    if months < 1 or min_pairs < 2 or not 0 < min_coverage <= 1:
        raise ValueError("Invalid analysis window or minimum coverage")
    home = housing.loc[housing.asset_id.eq("tehran_housing"),
                       ["jalali_period", "monthly_return", "data_quality_flag"]].copy()
    if home.empty or home.jalali_period.duplicated().any():
        raise ValueError("Missing or duplicate housing month")
    if reits.duplicated(["fund", "period"]).any() or set(FUNDS) - set(reits.fund):
        raise ValueError("Missing fund or duplicate fund/month return")
    end = home.jalali_period.max()
    if reits.period.max() < end:
        raise ValueError("REIT monthly returns end before housing")
    periods = [end]
    for _ in range(months - 1):
        periods.append(previous_month(periods[-1]))
    periods.reverse()
    home = home.loc[home.jalali_period.isin(periods)].rename(
        columns={"jalali_period": "period", "monthly_return": "housing_return"})
    home["housing_return"] = pd.to_numeric(home.housing_return, errors="coerce")
    required = max(min_pairs, ceil(months * min_coverage))
    pair_tables, estimates = [], []
    for fund in FUNDS:
        grid = pd.DataFrame({"period": periods})
        grid.insert(0, "fund", fund)
        sample = grid.merge(home, on="period", how="left", validate="many_to_one")
        own = reits.loc[reits.fund.eq(fund), ["period", "reinvested_return"]].copy()
        own["reinvested_return"] = pd.to_numeric(own.reinvested_return, errors="coerce")
        sample = sample.merge(own, on="period", how="left", validate="one_to_one")
        sample["paired"] = sample.housing_return.notna() & sample.reinvested_return.notna()
        pair_tables.append(sample)
        paired = sample.loc[sample.paired]
        n = len(paired)
        valid = n >= required and paired.housing_return.nunique() > 1 and paired.reinvested_return.nunique() > 1
        estimates.append({"fund": fund, "window_months": months,
                          "window_start": periods[0], "window_end": end,
                          "paired_months": n, "minimum_pairs": required,
                          "first_pair_month": paired.period.iloc[0] if n else "",
                          "last_pair_month": paired.period.iloc[-1] if n else "",
                          "correlation": paired.reinvested_return.corr(paired.housing_return) if valid else np.nan,
                          "status": "reported" if valid else "insufficient_pairs_or_variation",
                          "return_definition": "assembly_date_reinvested_traded_close_vs_housing_price_appreciation"})
    return pd.concat(pair_tables, ignore_index=True), pd.DataFrame(estimates)


def build() -> tuple[pd.DataFrame, pd.DataFrame]:
    housing = pd.read_csv(HOUSING, dtype={"jalali_period": str})
    reits = pd.read_csv(MONTHLY_RETURNS, dtype={"period": str})
    pairs, summary = analyze(housing, reits)
    atomic_frame(PAIRS, pairs)
    atomic_frame(SUMMARY, summary)
    return pairs, summary


if __name__ == "__main__":
    pairs, summary = build()
    print(f"Wrote {len(pairs)} fund/month rows; {summary.correlation.notna().sum()} of {len(summary)} correlations reported through {summary.window_end.iloc[0]}")
