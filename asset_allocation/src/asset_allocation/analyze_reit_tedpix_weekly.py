"""Build recent weekly returns and trailing correlations/regressions for REITs."""

from __future__ import annotations

import csv
import os
import tempfile
from datetime import date, datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

import jdatetime
import numpy as np
import pandas as pd
from scipy.stats import linregress

from asset_allocation.collectors.tsetmc_reits import MANIFEST, RAW

ROOT = Path(__file__).resolve().parents[2]
INDEX = ROOT / "data/raw/tse_total_index/tedpix_daily.csv"
PANEL = ROOT / "data/processed/analysis/reit_tedpix_weekly_returns.csv"
RESULTS = ROOT / "data/processed/analysis/reit_tedpix_weekly_windows.csv"
WINDOWS = (1, 3, 6, 12, 24)
ENGLISH_NAMES = {
    "45292762906823004": "Kelid", "71945594172117613": "Arzesh Maskan",
    "67717913151786055": "Danik", "71595553356620707": "Kakh",
    "41480981133648877": "Emarat Dey", "70814244102598215": "Amin Shahr",
    "37118058361762279": "Malek Atiyeh", "34322849244939912": "Kashaneh",
}


def friday(day: date) -> date:
    return day + timedelta(days=(4 - day.weekday()) % 7)


def shift_jalali_months(day: date, months: int) -> date:
    current = jdatetime.date.fromgregorian(date=day)
    serial = current.year * 12 + current.month - 1 - months
    year, month = divmod(serial, 12)
    month += 1
    try:
        shifted = jdatetime.date(year, month, current.day)
    except ValueError:
        shifted = jdatetime.date(year, month, 29 if month == 12 else 30)
    return shifted.togregorian()


def latest_complete_friday(path: Path = INDEX, as_of: date | None = None) -> date:
    with path.open(encoding="utf-8", newline="") as source:
        latest = max(date.fromisoformat(row["source_date_gregorian"]) for row in csv.DictReader(source))
    source_friday = friday(latest)
    today = as_of or datetime.now(ZoneInfo("Asia/Tehran")).date()
    elapsed_friday = today - timedelta(days=(today.weekday() - 4) % 7 or 7)
    return min(source_friday, elapsed_friday)


def weekly_closes(path: Path, field: str, earliest: date, anchor: date,
                  traded_only: bool = False) -> dict[date, dict[str, str]]:
    result = {}
    seen = set()
    with path.open(encoding="utf-8", newline="") as source:
        for row in csv.DictReader(source):
            observed = date.fromisoformat(row["source_date_gregorian"])
            if observed < earliest or observed > anchor:
                continue
            if observed in seen:
                raise ValueError(f"Duplicate daily observation in {path.name}: {observed}")
            seen.add(observed)
            if traded_only and row["has_trade"] != "true":
                continue
            value = float(row[field])
            if not np.isfinite(value) or value <= 0:
                raise ValueError(f"Invalid close in {path.name}: {observed}")
            week = friday(observed)
            if week <= anchor and (week not in result or observed.isoformat() > result[week]["source_date_gregorian"]):
                result[week] = row
    return result


def atomic_frame(path: Path, frame: pd.DataFrame) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", delete=False,
                                     dir=path.parent, suffix=".tmp") as file:
        frame.to_csv(file, index=False)
        temporary = Path(file.name)
    os.replace(temporary, path)


def build_panel(anchor: date | None = None) -> pd.DataFrame:
    anchor = anchor or latest_complete_friday()
    start = shift_jalali_months(anchor, 24)
    # One prior week is needed to calculate the first weekly return.
    earliest = start - timedelta(days=14)
    with MANIFEST.open(encoding="utf-8", newline="") as source:
        funds = list(csv.DictReader(source))
    series = [("equity_tedpix", "TEDPIX", weekly_closes(INDEX, "index_close", earliest, anchor), "index_close")]
    for fund in funds:
        code = fund["ins_code"]
        if code not in ENGLISH_NAMES:
            raise ValueError(f"English fund name required for instrument {code}")
        series.append((f"reit_{code}", ENGLISH_NAMES[code],
                       weekly_closes(RAW / f"{code}.csv", "closing_price_irr", earliest, anchor, True),
                       "closing_price_irr"))
    weeks = []
    week = friday(start)
    while week <= anchor:
        weeks.append(week)
        week += timedelta(days=7)
    rows = []
    for week in weeks:
        prior = week - timedelta(days=7)
        for asset, fund, closes, field in series:
            current, previous = closes.get(week), closes.get(prior)
            value = float(current[field]) / float(previous[field]) - 1 if current and previous else np.nan
            rows.append({"week_end_gregorian": week.isoformat(), "asset_id": asset, "fund": fund,
                         "source_observation_date": current["source_date_gregorian"] if current else "",
                         "weekly_return": value,
                         "missing_reason": "" if np.isfinite(value) else
                         ("no_trade_this_week" if not current else "no_trade_previous_week")})
    frame = pd.DataFrame(rows)
    atomic_frame(PANEL, frame)
    return frame


def analyze(panel: pd.DataFrame, anchor: date | None = None) -> pd.DataFrame:
    if panel.duplicated(["week_end_gregorian", "asset_id"]).any():
        raise ValueError("Duplicate week/asset")
    anchor = anchor or date.fromisoformat(panel.week_end_gregorian.max())
    wide = panel.pivot(index="week_end_gregorian", columns="asset_id", values="weekly_return")
    wide.index = pd.to_datetime(wide.index)
    names = panel.drop_duplicates("asset_id").set_index("asset_id").fund.to_dict()
    rows = []
    for asset in wide.columns.drop("equity_tedpix"):
        for months in WINDOWS:
            cutoff = shift_jalali_months(anchor, months)
            pair = wide.loc[(wide.index.date > cutoff) & (wide.index.date <= anchor),
                            ["equity_tedpix", asset]].dropna()
            result = {"asset_id": asset, "fund": names[asset], "window_months": months,
                      "window_start_gregorian": cutoff.isoformat(),
                      "window_end_gregorian": anchor.isoformat(), "overlap_weeks": len(pair),
                      "correlation": np.nan, "beta": np.nan, "alpha": np.nan,
                      "r_squared": np.nan, "p_value": np.nan}
            if len(pair) >= 3 and pair["equity_tedpix"].nunique() > 1 and pair[asset].nunique() > 1:
                fit = linregress(pair["equity_tedpix"], pair[asset])
                result.update(correlation=fit.rvalue, beta=fit.slope, alpha=fit.intercept,
                              r_squared=fit.rvalue ** 2, p_value=fit.pvalue)
            rows.append(result)
    frame = pd.DataFrame(rows)
    atomic_frame(RESULTS, frame)
    return frame


if __name__ == "__main__":
    weekly = build_panel()
    summary = analyze(weekly)
    print(f"Weekly panel: {len(weekly)} rows; {len(summary)} fund-window estimates; through {weekly.week_end_gregorian.max()}")
