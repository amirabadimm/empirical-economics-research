import pandas as pd

from asset_allocation.build_reit_assembly_reinvestment import reinvest_fund


def test_multiple_assembly_distributions_compound_on_next_traded_close():
    prices = pd.DataFrame({"source_date_gregorian": ["2025-01-01", "2025-01-03", "2025-02-01", "2025-02-03"],
                           "traded_close_irr": [100.0, 80.0, 90.0, 75.0]})
    events = pd.DataFrame({"assembly_date_gregorian": ["2025-01-02", "2025-02-02"],
                           "cash_irr_per_unit": [20.0, 15.0], "evidence_status": ["user_supplied"] * 2})
    panel, audit = reinvest_fund(prices, events)
    assert panel.reinvested_units.tolist() == [1.0, 1.25, 1.25, 1.5]
    assert panel.reinvested_value_irr.tolist() == [100.0, 100.0, 112.5, 112.5]
    assert audit.reinvestment_date_gregorian.tolist() == ["2025-01-03", "2025-02-03"]
