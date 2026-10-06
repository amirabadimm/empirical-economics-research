from datetime import date

import numpy as np
import pandas as pd

from asset_allocation.build_reit_requested_heatmaps import correlation_rows, dollar_lag_rows


def test_weekly_dollar_leads_reit_and_short_kakh_is_suppressed():
    weeks = pd.date_range("2023-01-06", "2026-10-02", freq="W-FRI")
    dollar = np.random.default_rng(7).normal(size=len(weeks))
    usd = pd.DataFrame({"period": weeks.strftime("%Y-%m-%d"), "return": dollar})
    rows = []
    for fund in ("Arzesh Maskan", "Kelid", "Danik", "Kakh"):
        start = len(weeks) - 4 if fund == "Kakh" else 4
        rows.extend({"fund": fund, "period": weeks[i].strftime("%Y-%m-%d"),
                     "reinvested_return": dollar[i - 4]} for i in range(start, len(weeks)))
    result = pd.DataFrame(dollar_lag_rows(pd.DataFrame(rows), usd, date(2026, 10, 2)))
    arzesh = result.loc[result.fund.eq("Arzesh Maskan")].set_index("lag_weeks")
    assert np.isclose(arzesh.loc[4, "correlation"], 1)
    assert abs(arzesh.loc[13, "correlation"]) < 0.5
    assert result.loc[result.fund.eq("Kakh"), "correlation"].isna().all()


def test_five_pairs_alone_do_not_claim_twelve_month_coverage():
    months = [f"1405/{i:02d}" for i in range(1, 7)]
    reits = pd.DataFrame([{"fund": fund, "period": period, "reinvested_return": i / 100}
                          for fund in ("Arzesh Maskan", "Kelid", "Danik", "Kakh")
                          for i, period in enumerate(months, 1)])
    housing = pd.DataFrame({"period": months, "return": np.arange(6) / 50})
    result = pd.DataFrame(correlation_rows(reits, housing, name="Tehran housing",
                                           frequency="monthly", anchor=date(2026, 10, 2),
                                           windows=(12,)))
    assert result.paired_observations.eq(6).all()
    assert result.minimum_pairs.eq(9).all()
    assert result.correlation.isna().all()
