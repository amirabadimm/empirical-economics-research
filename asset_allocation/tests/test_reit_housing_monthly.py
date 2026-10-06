import numpy as np
import pandas as pd

from asset_allocation.analyze_reit_housing_monthly import analyze


def test_exact_month_matching_and_short_fund_suppression():
    months = [f"1405/{number:02}" for number in range(1, 7)]
    housing = pd.DataFrame({"asset_id": "tehran_housing", "jalali_period": months,
                            "monthly_return": [0.01, 0.03, -0.02, 0.04, 0.00, 0.02],
                            "data_quality_flag": "secondary_proxy_low_overlap_similarity"})
    rows = []
    for fund in ("Arzesh Maskan", "Kelid", "Danik"):
        for period, ret in zip(months, housing.monthly_return):
            rows.append({"fund": fund, "period": period, "reinvested_return": ret * 2})
    for period, ret in zip(months[-2:], [0.05, -0.01]):
        rows.append({"fund": "Kakh", "period": period, "reinvested_return": ret})
    pairs, summary = analyze(housing, pd.DataFrame(rows), months=6, min_pairs=4)
    assert len(pairs) == 24
    assert summary.set_index("fund").loc["Arzesh Maskan", "paired_months"] == 6
    assert np.isclose(summary.set_index("fund").loc["Arzesh Maskan", "correlation"], 1.0)
    assert summary.set_index("fund").loc["Kakh", "paired_months"] == 2
    assert np.isnan(summary.set_index("fund").loc["Kakh", "correlation"])
    assert pairs.loc[(pairs.fund == "Kakh") & (pairs.period == "1405/01"), "paired"].item() == False
