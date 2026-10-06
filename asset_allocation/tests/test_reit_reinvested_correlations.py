from datetime import date

import numpy as np
import pandas as pd

from asset_allocation.build_reit_reinvested_correlations import returns


def test_weekly_return_uses_reinvested_levels_and_requires_adjacent_weeks():
    frame = pd.DataFrame({"date": [date(2026, 1, 2), date(2026, 1, 9), date(2026, 1, 23)],
                          "level": [100.0, 125.0, 150.0]})
    result = returns(frame, "weekly", date(2026, 1, 23))
    assert np.isclose(result.iloc[1]["return"], 0.25)
    assert np.isnan(result.iloc[2]["return"])


def test_usd_method_boundary_is_excluded():
    frame = pd.DataFrame({"date": [date(2026, 1, 2), date(2026, 1, 9)],
                          "level": [100.0, 120.0], "price_method": ["old", "new"]})
    result = returns(frame, "weekly", date(2026, 1, 9), usd=True)
    assert np.isnan(result.iloc[1]["return"])
