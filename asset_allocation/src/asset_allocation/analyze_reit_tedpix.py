"""Trailing-window correlations and OLS of fund returns on TEDPIX returns."""

from __future__ import annotations

from pathlib import Path
import os
import tempfile

import numpy as np
import pandas as pd
from scipy.stats import linregress

PANEL = Path(__file__).resolve().parents[2] / "data/processed/analysis/reit_tedpix_monthly_returns.csv"
OUTPUT = PANEL.with_name("reit_tedpix_trailing_windows.csv")
WINDOWS = (1, 3, 6, 12, 24, 48)
INDEX_ID = "equity_tedpix"


def analyze(panel: pd.DataFrame, windows: tuple[int, ...] = WINDOWS) -> pd.DataFrame:
    required = {"jalali_period", "asset_id", "ticker", "monthly_return"}
    if not required.issubset(panel.columns):
        raise ValueError(f"Missing panel columns: {required - set(panel.columns)}")
    if panel.duplicated(["jalali_period", "asset_id"]).any():
        raise ValueError("Duplicate month/asset in return panel")
    index_rows = panel.loc[panel.asset_id == INDEX_ID]
    if index_rows.empty:
        raise ValueError("TEDPIX is absent")
    # The last observed Jalali month is potentially still in progress.
    complete = panel.loc[panel.jalali_period < panel.jalali_period.max()].copy()
    periods = sorted(complete.jalali_period.unique())
    wide = complete.pivot(index="jalali_period", columns="asset_id", values="monthly_return")
    wide = wide.apply(pd.to_numeric, errors="coerce")
    tickers = complete.drop_duplicates("asset_id").set_index("asset_id").ticker.to_dict()
    rows = []
    for asset_id, ticker in tickers.items():
        if asset_id == INDEX_ID:
            continue
        for window in windows:
            months = periods[-window:]
            pair = wide.loc[months, [INDEX_ID, asset_id]].dropna()
            n = len(pair)
            result = {"asset_id": asset_id, "ticker": ticker, "window_months": window,
                      "window_start": months[0], "window_end": months[-1], "overlap_months": n,
                      "correlation": np.nan, "beta": np.nan, "alpha": np.nan,
                      "r_squared": np.nan, "p_value": np.nan}
            if window > 1 and n >= 3 and pair[INDEX_ID].nunique() > 1 and pair[asset_id].nunique() > 1:
                fit = linregress(pair[INDEX_ID], pair[asset_id])
                result.update(correlation=fit.rvalue, beta=fit.slope, alpha=fit.intercept,
                              r_squared=fit.rvalue ** 2, p_value=fit.pvalue)
            rows.append(result)
    return pd.DataFrame(rows)


def load_and_analyze(path: Path = PANEL) -> pd.DataFrame:
    return analyze(pd.read_csv(path, dtype={"jalali_period": str, "asset_id": str}))


def write_results(path: Path = OUTPUT) -> pd.DataFrame:
    result = load_and_analyze()
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", delete=False,
                                     dir=path.parent, suffix=".tmp") as file:
        result.to_csv(file, index=False)
        temporary = Path(file.name)
    os.replace(temporary, path)
    return result


if __name__ == "__main__":
    table = write_results()
    print(f"Wrote {len(table)} fund-window rows to {OUTPUT}")
