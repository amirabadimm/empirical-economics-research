from datetime import date

import numpy as np
import pandas as pd

from asset_allocation.analyze_reit_usd_weekly_predictive import aligned_weekly, analyze


def test_weekly_lags_follow_friday_grid_and_share_same_pairs():
    weeks = pd.date_range("2026-01-02", periods=18, freq="W-FRI")
    labels = weeks.strftime("%Y-%m-%d")
    usd = pd.DataFrame({"period": labels, "return": np.sin(np.arange(18) * 0.7) * 0.02})
    usd = usd.drop(index=5)  # Missing calendar week must stay missing under every shift.
    tedpix = pd.DataFrame({"period": labels, "return": np.cos(np.arange(18) * 0.5) * 0.01})
    reits = pd.DataFrame({"fund": "Kelid", "period": labels,
                          "reinvested_return": np.sin(np.arange(18) * 0.31) * 0.03})
    panel, cutoff = aligned_weekly(reits, usd, tedpix, date(2026, 5, 1), months=5)
    assert pd.isna(panel.loc["2026-02-13", "usd_l1"])
    lags, models = analyze(panel, cutoff, date(2026, 5, 1),
                           min_correlation_pairs=5, min_regression_pairs=8)
    assert lags.paired_weeks.nunique() == 1
    assert lags.correlation.notna().sum() == 5
    assert models.status.iloc[0] == "reported"
    assert "joint_usd_fdr_pvalue" not in models.columns
