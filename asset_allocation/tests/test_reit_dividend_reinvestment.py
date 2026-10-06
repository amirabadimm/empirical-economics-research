import pandas as pd

from asset_allocation.build_reit_dividend_reinvestment import reinvest


def test_reinvests_on_first_traded_close_after_payment():
    prices = pd.DataFrame({"source_date_gregorian": ["2026-01-01", "2026-01-03", "2026-01-05"],
                           "unadjusted_close_irr": [100.0, 80.0, 90.0]})
    events = pd.DataFrame({"payment_date_gregorian": ["2026-01-02"], "cash_irr_per_unit": [20.0]})
    result = reinvest(prices, events)
    assert result.reinvested_units.tolist() == [1.0, 1.25, 1.25]
    assert result.reinvested_value_irr.tolist() == [100.0, 100.0, 112.5]
