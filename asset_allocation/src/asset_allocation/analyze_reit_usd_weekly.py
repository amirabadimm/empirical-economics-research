"""Weekly REIT regressions on the shared USD/IRR price in rials per dollar."""

from __future__ import annotations

import csv
from datetime import date, timedelta
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import linregress

from asset_allocation.analyze_reit_tedpix_weekly import (
    PANEL as FUND_PANEL, WINDOWS, atomic_frame, friday, shift_jalali_months,
)

WORKSPACE = Path(__file__).resolve().parents[3]
USD_RAW = WORKSPACE / "shared/data/raw/fx/usd_to_rial.csv"
OUTPUT_DIR = WORKSPACE / "asset_allocation/data/processed/analysis"
USD_PANEL = OUTPUT_DIR / "usd_irr_weekly_returns.csv"
RESULTS = OUTPUT_DIR / "reit_usd_weekly_windows.csv"


def usd_weekly_closes(path: Path, earliest: date, anchor: date) -> dict[date, dict]:
    closes: dict[date, dict] = {}
    seen = set()
    with path.open(encoding="utf-8-sig", newline="") as source:
        for row in csv.DictReader(source):
            y, m, d = map(int, row["date_gr"].replace("-", "/").split("/"))
            observed = date(y, m, d)
            if observed < earliest or observed > anchor:
                continue
            if observed in seen:
                raise ValueError(f"Duplicate USD/IRR observation: {observed}")
            seen.add(observed)
            price = float(row["price_irr"].replace(",", ""))
            if not np.isfinite(price) or price <= 0:
                raise ValueError(f"Invalid USD/IRR price on {observed}")
            week = friday(observed)
            if week <= anchor and (week not in closes or observed > closes[week]["observed"]):
                closes[week] = {"observed": observed, "price": price,
                                "method": row["price_method"], "source": row["source"]}
    return closes


def build_usd_panel(fund_panel: pd.DataFrame, path: Path = USD_RAW) -> pd.DataFrame:
    weeks = sorted(date.fromisoformat(x) for x in fund_panel.week_end_gregorian.unique())
    anchor = weeks[-1]
    closes = usd_weekly_closes(path, weeks[0] - timedelta(days=14), anchor)
    rows = []
    for week in weeks:
        current, previous = closes.get(week), closes.get(week - timedelta(days=7))
        method_change = bool(current and previous and current["method"] != previous["method"])
        valid = current and previous and not method_change
        value = current["price"] / previous["price"] - 1 if valid else np.nan
        rows.append({"week_end_gregorian": week.isoformat(),
                     "source_observation_date": current["observed"].isoformat() if current else "",
                     "usd_irr_level": current["price"] if current else np.nan,
                     "usd_irr_weekly_return": value,
                     "price_method": current["method"] if current else "",
                     "previous_price_method": previous["method"] if previous else "",
                     "method_change": method_change,
                     "missing_reason": "" if valid else ("method_change" if method_change else
                                      "no_usd_observation_this_week" if not current else
                                      "no_usd_observation_previous_week")})
    frame = pd.DataFrame(rows)
    atomic_frame(USD_PANEL, frame)
    return frame


def analyze(fund_panel: pd.DataFrame, usd_panel: pd.DataFrame) -> pd.DataFrame:
    if fund_panel.duplicated(["week_end_gregorian", "asset_id"]).any():
        raise ValueError("Duplicate fund week/asset")
    if usd_panel.duplicated("week_end_gregorian").any():
        raise ValueError("Duplicate USD week")
    anchor = date.fromisoformat(fund_panel.week_end_gregorian.max())
    funds = fund_panel.loc[fund_panel.asset_id != "equity_tedpix"].merge(
        usd_panel[["week_end_gregorian", "usd_irr_weekly_return", "price_method"]],
        on="week_end_gregorian", validate="many_to_one")
    funds["weekly_return"] = pd.to_numeric(funds.weekly_return, errors="coerce")
    rows = []
    for asset, group in funds.groupby("asset_id", sort=False):
        for months in WINDOWS:
            cutoff = shift_jalali_months(anchor, months)
            sample = group.loc[(group.week_end_gregorian > cutoff.isoformat()) &
                               (group.week_end_gregorian <= anchor.isoformat())].dropna(
                                   subset=["weekly_return", "usd_irr_weekly_return"])
            result = {"asset_id": asset, "fund": group.fund.iloc[0], "window_months": months,
                      "window_start_gregorian": cutoff.isoformat(),
                      "window_end_gregorian": anchor.isoformat(), "overlap_weeks": len(sample),
                      "legacy_midpoint_weeks": int((sample.price_method == "legacy_high_low_midpoint").sum()),
                      "close_weeks": int((sample.price_method == "close").sum()),
                      "correlation": np.nan, "beta": np.nan, "alpha": np.nan,
                      "r_squared": np.nan, "p_value": np.nan}
            if len(sample) >= 3 and sample.usd_irr_weekly_return.nunique() > 1 and sample.weekly_return.nunique() > 1:
                fit = linregress(sample.usd_irr_weekly_return, sample.weekly_return)
                result.update(correlation=fit.rvalue, beta=fit.slope, alpha=fit.intercept,
                              r_squared=fit.rvalue ** 2, p_value=fit.pvalue)
            rows.append(result)
    frame = pd.DataFrame(rows)
    atomic_frame(RESULTS, frame)
    return frame


if __name__ == "__main__":
    funds = pd.read_csv(FUND_PANEL, dtype={"week_end_gregorian": str, "asset_id": str})
    usd = build_usd_panel(funds)
    results = analyze(funds, usd)
    print(f"USD weekly observations: {usd.usd_irr_weekly_return.notna().sum()}; "
          f"fund/window estimates: {len(results)}; through {usd.week_end_gregorian.max()}")
