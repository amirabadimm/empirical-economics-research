"""Bounded USD lead-lag correlations and predictive regressions for reconstructed REIT returns."""

from __future__ import annotations

from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm
from statsmodels.stats.multitest import multipletests

from asset_allocation.analyze_reit_tedpix_weekly import atomic_frame, latest_complete_friday, shift_jalali_months
from asset_allocation.build_reit_reinvested_correlations import TEDPIX, USD, WEEKLY_RETURNS, returns

ROOT = Path(__file__).resolve().parents[2]
LAGS = ROOT / "data/processed/analysis/reit_usd_weekly_lag_correlations.csv"
REGRESSIONS = ROOT / "data/processed/analysis/reit_usd_weekly_predictive_regressions.csv"
MAX_USD_LAG = 4
MIN_CORRELATION_PAIRS = 74  # At least 70% of roughly 105 weeks in 24 Jalali months.
MIN_REGRESSION_PAIRS = 52


def aligned_weekly(reits: pd.DataFrame, usd: pd.DataFrame, tedpix: pd.DataFrame,
                   anchor: date, months: int = 24) -> tuple[pd.DataFrame, date]:
    """Build a complete Friday grid before shifting so a lag is a calendar week."""
    cutoff = shift_jalali_months(anchor, months)
    first = pd.Timestamp(cutoff) - pd.Timedelta(weeks=MAX_USD_LAG + 2)
    weeks = pd.date_range(first, anchor, freq="W-FRI").strftime("%Y-%m-%d")
    panel = pd.DataFrame(index=pd.Index(weeks, name="period"))
    for name, values in (("usd", usd), ("tedpix", tedpix)):
        if values.period.duplicated().any():
            raise ValueError(f"Duplicate {name} weekly period")
        panel[name] = values.set_index("period")["return"].reindex(panel.index)
    for fund, group in reits.groupby("fund"):
        if group.period.duplicated().any():
            raise ValueError(f"Duplicate {fund} weekly period")
        panel[fund] = group.set_index("period")["reinvested_return"].reindex(panel.index)
    for lag in range(MAX_USD_LAG + 1):
        panel[f"usd_l{lag}"] = panel.usd.shift(lag)
    panel["tedpix_l1"] = panel.tedpix.shift(1)
    return panel.loc[(panel.index > cutoff.isoformat()) & (panel.index <= anchor.isoformat())], cutoff


def analyze(panel: pd.DataFrame, cutoff: date, anchor: date,
            min_correlation_pairs: int = MIN_CORRELATION_PAIRS,
            min_regression_pairs: int = MIN_REGRESSION_PAIRS) -> tuple[pd.DataFrame, pd.DataFrame]:
    lag_rows, model_rows = [], []
    funds = [column for column in panel if column not in
             {"usd", "tedpix", "tedpix_l1", *(f"usd_l{i}" for i in range(MAX_USD_LAG + 1))}]
    for fund in sorted(funds):
        # All five correlations use the exact same dates for this fund.
        common = panel[[fund] + [f"usd_l{i}" for i in range(MAX_USD_LAG + 1)]].dropna()
        sufficient = len(common) >= min_correlation_pairs
        for lag in range(MAX_USD_LAG + 1):
            x = common[f"usd_l{lag}"]
            valid = sufficient and x.nunique() > 1 and common[fund].nunique() > 1
            lag_rows.append({"fund": fund, "usd_lag_weeks": lag,
                             "paired_weeks": len(common),
                             "first_pair_week": common.index.min() if len(common) else "",
                             "last_pair_week": common.index.max() if len(common) else "",
                             "window_start": cutoff.isoformat(), "window_end": anchor.isoformat(),
                             "correlation": common[fund].corr(x) if valid else np.nan,
                             "status": "reported" if valid else "insufficient_common_weeks_or_variation",
                             "return_definition": "assembly_date_reinvested_traded_close_scenario"})
        regress = panel[[fund, "usd_l1", "usd_l2", "tedpix_l1"]].copy()
        regress["reit_l1"] = panel[fund].shift(1)
        regress = regress.dropna()
        row = {"fund": fund, "paired_weeks": len(regress),
               "first_pair_week": regress.index.min() if len(regress) else "",
               "last_pair_week": regress.index.max() if len(regress) else "",
               "window_start": cutoff.isoformat(), "window_end": anchor.isoformat(),
               "beta_usd_l1": np.nan, "beta_usd_l2": np.nan,
               "beta_reit_l1": np.nan, "beta_tedpix_l1": np.nan,
               "joint_usd_pvalue": np.nan, "r_squared": np.nan,
               "baseline_r_squared": np.nan, "incremental_r_squared": np.nan,
               "status": "insufficient_weeks", "hac_maxlags": 4,
               "return_definition": "assembly_date_reinvested_traded_close_scenario"}
        if len(regress) >= min_regression_pairs and regress[fund].nunique() > 1:
            y = regress[fund]
            full_x = sm.add_constant(regress[["reit_l1", "usd_l1", "usd_l2", "tedpix_l1"]])
            base_x = sm.add_constant(regress[["reit_l1", "tedpix_l1"]])
            if np.linalg.matrix_rank(full_x.to_numpy()) == full_x.shape[1]:
                fit = sm.OLS(y, full_x).fit(cov_type="HAC", cov_kwds={"maxlags": 4})
                base = sm.OLS(y, base_x).fit()
                test = fit.wald_test("usd_l1 = 0, usd_l2 = 0", scalar=True)
                row.update(beta_usd_l1=fit.params["usd_l1"], beta_usd_l2=fit.params["usd_l2"],
                           beta_reit_l1=fit.params["reit_l1"], beta_tedpix_l1=fit.params["tedpix_l1"],
                           joint_usd_pvalue=float(test.pvalue), r_squared=fit.rsquared,
                           baseline_r_squared=base.rsquared,
                           incremental_r_squared=fit.rsquared - base.rsquared, status="reported")
            else:
                row["status"] = "singular_design"
        model_rows.append(row)
    models = pd.DataFrame(model_rows)
    models["joint_usd_fdr_pvalue"] = np.nan
    eligible = models.joint_usd_pvalue.notna()
    if eligible.any():
        models.loc[eligible, "joint_usd_fdr_pvalue"] = multipletests(
            models.loc[eligible, "joint_usd_pvalue"], method="fdr_bh")[1]
    return pd.DataFrame(lag_rows), models


def build(anchor: date | None = None) -> tuple[pd.DataFrame, pd.DataFrame]:
    anchor = anchor or latest_complete_friday()
    reits = pd.read_csv(WEEKLY_RETURNS)
    fx = pd.read_csv(USD)
    fx["date"] = pd.to_datetime(fx.date_gr.str.replace("/", "-", regex=False)).dt.date
    fx["level"] = pd.to_numeric(fx.price_irr.str.replace(",", "", regex=False))
    usd = returns(fx, "weekly", anchor, usd=True)
    index = pd.read_csv(TEDPIX)
    index["date"] = pd.to_datetime(index.source_date_gregorian).dt.date
    index["level"] = pd.to_numeric(index.index_close)
    tedpix = returns(index, "weekly", anchor)
    panel, cutoff = aligned_weekly(reits, usd, tedpix, anchor)
    lags, regressions = analyze(panel, cutoff, anchor)
    atomic_frame(LAGS, lags)
    atomic_frame(REGRESSIONS, regressions)
    return lags, regressions


if __name__ == "__main__":
    lags, regressions = build()
    print(f"Lag correlations: {lags.correlation.notna().sum()}/{len(lags)}; predictive regressions: {(regressions.status == 'reported').sum()}/{len(regressions)}")
