from datetime import date

import numpy as np
import pandas as pd

from asset_allocation.analyze_reit_usd_lags import pair_lags, price_returns, previous_month


def test_prior_day_requires_exact_dollar_date_and_skips_method_boundary():
    fund = pd.DataFrame({"date": [date(2026, 1, 3), date(2026, 1, 4), date(2026, 1, 6)],
                         "level": [100, 110, 121]})
    usd = pd.DataFrame({"date": [date(2026, 1, 2), date(2026, 1, 3), date(2026, 1, 4), date(2026, 1, 6)],
                        "level": [100, 110, 120, 130],
                        "price_method": ["legacy", "legacy", "close", "close"]})
    f = price_returns(fund, "day", False)
    u = price_returns(usd, "day", True)
    paired = pair_lags(f, u, "day", "Danik")
    lagged = paired.loc[paired.lag_periods == 1].set_index("period")
    assert np.isclose(lagged.loc["2026-01-04", "usd_return"], 0.1)
    assert pd.isna(lagged.loc["2026-01-06", "usd_return"])
    assert pd.isna(u.loc[u.period == "2026-01-04", "return"].iloc[0])


def test_month_lag_uses_prior_jalali_period():
    assert previous_month("1405/01") == "1404/12"
    fund = pd.DataFrame({"period": ["1405/02"], "date": [date(2026, 5, 20)],
                         "return": [0.05], "price_method": ["traded_close"]})
    usd = pd.DataFrame({"period": ["1405/01"], "date": [date(2026, 4, 20)],
                        "return": [0.03], "price_method": ["close"]})
    paired = pair_lags(fund, usd, "month", "Kelid")
    assert paired.loc[paired.lag_periods == 1, "usd_return"].iloc[0] == 0.03
    assert pd.isna(paired.loc[paired.lag_periods == 0, "usd_return"].iloc[0])
