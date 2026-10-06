import math

import pandas as pd

from asset_allocation.analyze_reit_tedpix import analyze


def test_trailing_windows_exclude_current_month_and_regress_on_overlap():
    months = [f"1404/{m:02}" for m in range(1, 7)]
    index = [0.01, 0.03, -0.02, 0.04, 0.00, 0.50]
    fund = [0.04, 0.08, -0.02, 0.10, None, 10.0]
    rows = []
    for month, x, y in zip(months, index, fund):
        rows.extend([{"jalali_period": month, "asset_id": "equity_tedpix", "ticker": "شاخص کل", "monthly_return": x},
                     {"jalali_period": month, "asset_id": "reit_1", "ticker": "fund", "monthly_return": y}])
    result = analyze(pd.DataFrame(rows), windows=(1, 3, 6))
    one, three, six = (result.loc[result.window_months == w].iloc[0] for w in (1, 3, 6))
    assert one.overlap_months == 0 and math.isnan(one.correlation)
    assert three.window_start == "1404/03" and three.window_end == "1404/05"
    assert three.overlap_months == 2 and math.isnan(three.beta)
    assert six.overlap_months == 4
    assert math.isclose(six.beta, 2.0)
    assert math.isclose(six.alpha, 0.02)
    assert math.isclose(six.correlation, 1.0)
    assert math.isclose(six.r_squared, 1.0)


def test_duplicate_month_asset_is_rejected():
    panel = pd.DataFrame([{"jalali_period": "1404/01", "asset_id": "equity_tedpix",
                           "ticker": "شاخص کل", "monthly_return": 0.1}] * 2)
    try:
        analyze(panel)
    except ValueError as exc:
        assert "Duplicate" in str(exc)
    else:
        raise AssertionError("Expected duplicate month/asset rejection")
