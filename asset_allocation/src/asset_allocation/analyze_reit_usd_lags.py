"""Dollar/REIT correlations at zero and one day, week, or Jalali-month lag."""

from __future__ import annotations

import csv
from datetime import date, timedelta
from pathlib import Path

import jdatetime
import numpy as np
import pandas as pd

from asset_allocation.analyze_reit_tedpix_weekly import atomic_frame, friday, latest_complete_friday, shift_jalali_months

ROOT = Path(__file__).resolve().parents[2]
FX = ROOT.parent / "shared/data/raw/fx/usd_to_rial.csv"
FUND_RAW = ROOT / "data/raw/real_estate_funds"
OUT = ROOT / "data/processed/analysis"
PAIRS = OUT / "three_reit_usd_lag_pairs.csv"
RESULTS = OUT / "three_reit_usd_lag_correlations.csv"
FUNDS = {"71945594172117613": "Arzesh Maskan", "45292762906823004": "Kelid",
         "67717913151786055": "Danik"}
WINDOWS = (1, 3, 6, 12, 24, 48)


def jalali_period(day: date) -> str:
    jalali = jdatetime.date.fromgregorian(date=day)
    return f"{jalali.year:04d}/{jalali.month:02d}"


def previous_month(period: str) -> str:
    year, month = map(int, period.split("/"))
    return f"{year - 1:04d}/12" if month == 1 else f"{year:04d}/{month - 1:02d}"


def read_fx(path: Path, start: date, anchor: date) -> pd.DataFrame:
    with path.open(encoding="utf-8-sig", newline="") as file:
        rows = list(csv.DictReader(file))
    frame = pd.DataFrame(rows)
    frame["date"] = pd.to_datetime(frame.date_gr.str.replace("/", "-", regex=False), errors="raise").dt.date
    frame = frame.loc[frame.date.between(start, anchor)].copy()
    frame["level"] = pd.to_numeric(frame.price_irr.str.replace(",", "", regex=False), errors="raise")
    if frame.date.duplicated().any() or (frame.level <= 0).any():
        raise ValueError("Duplicate or nonpositive USD observation")
    return frame.sort_values("date")


def read_fund(path: Path, start: date, anchor: date) -> pd.DataFrame:
    frame = pd.read_csv(path, dtype={"source_date_gregorian": str})
    frame["date"] = pd.to_datetime(frame.source_date_gregorian, errors="raise").dt.date
    frame = frame.loc[frame.date.between(start, anchor) & frame.has_trade.eq(True)].copy()
    frame["level"] = pd.to_numeric(frame.closing_price_irr, errors="raise")
    if frame.date.duplicated().any() or (frame.level <= 0).any():
        raise ValueError(f"Duplicate or nonpositive traded close in {path.name}")
    return frame.sort_values("date")


def price_returns(frame: pd.DataFrame, frequency: str, fx: bool) -> pd.DataFrame:
    data = frame.copy()
    if frequency == "day":
        data["period"] = data.date.map(date.isoformat)
    elif frequency == "week":
        data["period"] = data.date.map(lambda day: friday(day).isoformat())
        data = data.sort_values("date").groupby("period", as_index=False).tail(1)
    else:
        data["period"] = data.date.map(jalali_period)
        data = data.sort_values("date").groupby("period", as_index=False).tail(1)
    data = data.sort_values("period").copy()
    data["previous_period"] = data.period.shift(1)
    data["previous_level"] = data.level.shift(1)
    if fx:
        data["previous_method"] = data.price_method.shift(1)
    else:
        data["previous_method"] = ""
        data["price_method"] = "traded_close"
    def adjacent(row: pd.Series) -> bool:
        prior = row.previous_period
        if pd.isna(prior):
            return False
        if frequency == "day":
            # Daily means consecutive observed sessions, allowing exchange holidays.
            return (date.fromisoformat(row.period) - date.fromisoformat(prior)).days <= 5
        if frequency == "week":
            return (date.fromisoformat(row.period) - date.fromisoformat(prior)).days == 7
        return previous_month(row.period) == prior
    data["adjacent"] = data.apply(adjacent, axis=1)
    if fx:
        data["adjacent"] &= data.price_method.eq(data.previous_method)
    data["return"] = np.where(data.adjacent, data.level / data.previous_level - 1, np.nan)
    return data[["period", "date", "return", "price_method"]].reset_index(drop=True)


def pair_lags(fund: pd.DataFrame, usd: pd.DataFrame, frequency: str, name: str) -> pd.DataFrame:
    dollar = usd.rename(columns={"period": "usd_period", "return": "usd_return",
                                 "price_method": "usd_price_method", "date": "usd_observation_date"})
    rows = []
    for lag in (0, 1):
        sample = fund.copy()
        if frequency == "day":
            sample["usd_period"] = sample.period.map(
                lambda x: (date.fromisoformat(x) - timedelta(days=lag)).isoformat())
        elif frequency == "week":
            sample["usd_period"] = sample.period.map(
                lambda x: (date.fromisoformat(x) - timedelta(days=7 * lag)).isoformat())
        else:
            sample["usd_period"] = sample.period if lag == 0 else sample.period.map(previous_month)
        sample = sample.merge(dollar, on="usd_period", how="left", validate="many_to_one")
        sample.insert(0, "fund", name)
        sample.insert(1, "frequency", frequency)
        sample.insert(2, "lag_periods", lag)
        sample = sample.rename(columns={"return": "fund_return", "date": "fund_observation_date"})
        rows.append(sample[["fund", "frequency", "lag_periods", "period", "fund_observation_date",
                            "fund_return", "usd_period", "usd_observation_date", "usd_return", "usd_price_method"]])
    return pd.concat(rows, ignore_index=True)


def correlate(pairs: pd.DataFrame, anchor: date) -> pd.DataFrame:
    rows = []
    complete_month = previous_month(jalali_period(anchor))
    for (fund, frequency, lag), group in pairs.groupby(["fund", "frequency", "lag_periods"], sort=True):
        for months in WINDOWS:
            cutoff = shift_jalali_months(anchor, months)
            if frequency == "month":
                end = complete_month
                # A trailing N-month window is the last N complete Jalali periods.
                periods = []
                cursor = end
                for _ in range(months):
                    periods.append(cursor)
                    cursor = previous_month(cursor)
                window = group.loc[group.period.isin(periods)]
                start_label = periods[-1]
            else:
                window = group.loc[(group.period > cutoff.isoformat()) &
                                   (group.period <= anchor.isoformat())]
                end = anchor.isoformat()
                start_label = cutoff.isoformat()
            paired = window.dropna(subset=["fund_return", "usd_return"])
            coefficient = np.nan
            if len(paired) >= 3 and paired.fund_return.nunique() > 1 and paired.usd_return.nunique() > 1:
                coefficient = paired.fund_return.corr(paired.usd_return)
            rows.append({"fund": fund, "frequency": frequency, "lag_periods": lag,
                         "window_months": months, "window_start": start_label, "window_end": end,
                         "paired_observations": len(paired), "correlation": coefficient,
                         "legacy_midpoint_pairs": int((paired.usd_price_method == "legacy_high_low_midpoint").sum()),
                         "close_pairs": int((paired.usd_price_method == "close").sum()),
                         "return_definition": "traded_fund_close_change_usd_return_source_boundary_excluded"})
    return pd.DataFrame(rows)


def build(anchor: date | None = None, fx_path: Path = FX, fund_raw: Path = FUND_RAW) -> tuple[pd.DataFrame, pd.DataFrame]:
    anchor = anchor or latest_complete_friday()
    start = shift_jalali_months(anchor, 48) - timedelta(days=45)
    fx = read_fx(fx_path, start, anchor)
    complete_month = previous_month(jalali_period(anchor))
    output = []
    for frequency in ("day", "week", "month"):
        dollar = price_returns(fx, frequency, True)
        if frequency == "month":
            dollar = dollar.loc[dollar.period <= complete_month]
        for code, name in FUNDS.items():
            fund = price_returns(read_fund(fund_raw / f"{code}.csv", start, anchor), frequency, False)
            if frequency == "month":
                fund = fund.loc[fund.period <= complete_month]
            output.append(pair_lags(fund, dollar, frequency, name))
    pairs = pd.concat(output, ignore_index=True)
    results = correlate(pairs, anchor)
    atomic_frame(PAIRS, pairs)
    atomic_frame(RESULTS, results)
    return pairs, results


if __name__ == "__main__":
    pairs, results = build()
    print(f"Wrote {len(pairs)} return-pair rows and {len(results)} correlation cells")
