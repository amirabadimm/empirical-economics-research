import csv
from datetime import date

import pandas as pd

from asset_allocation import analyze_reit_usd_weekly as fx


def test_weekly_usd_uses_rials_and_excludes_method_boundary(tmp_path, monkeypatch):
    raw = tmp_path / "usd.csv"
    with raw.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=["date_gr", "price_irr", "price_method", "source"])
        writer.writeheader()
        writer.writerows([
            {"date_gr": "2026/9/18", "price_irr": "1,000,000", "price_method": "legacy_high_low_midpoint", "source": "legacy"},
            {"date_gr": "2026/9/24", "price_irr": "1,100,000", "price_method": "close", "source": "tgju"},
            {"date_gr": "2026/10/1", "price_irr": "1,210,000", "price_method": "close", "source": "tgju"},
        ])
    monkeypatch.setattr(fx, "atomic_frame", lambda path, frame: None)
    funds = pd.DataFrame({"week_end_gregorian": ["2026-09-18", "2026-09-25", "2026-10-02"]})
    panel = fx.build_usd_panel(funds, raw)
    assert pd.isna(panel.iloc[1].usd_irr_weekly_return)
    assert panel.iloc[1].missing_reason == "method_change"
    assert abs(panel.iloc[2].usd_irr_weekly_return - 0.1) < 1e-12
    assert panel.iloc[2].usd_irr_level == 1_210_000


def test_fund_regression_uses_usd_as_explanatory_return(monkeypatch):
    monkeypatch.setattr(fx, "atomic_frame", lambda path, frame: None)
    weeks = pd.date_range("2026-08-07", periods=5, freq="7D").strftime("%Y-%m-%d").tolist()
    usd = pd.DataFrame({"week_end_gregorian": weeks, "usd_irr_weekly_return": [0.01, 0.02, -0.01, 0.03, 0.04],
                        "price_method": ["close"] * 5})
    funds = pd.DataFrame({"week_end_gregorian": weeks, "asset_id": ["reit_1"] * 5,
                          "fund": ["Fund"] * 5,
                          "weekly_return": [0.03, 0.05, -0.01, 0.07, 0.09]})
    result = fx.analyze(funds, usd)
    row = result.loc[result.window_months == 3].iloc[0]
    assert row.overlap_weeks == 5
    assert abs(row.beta - 2) < 1e-12
    assert abs(row.alpha - 0.01) < 1e-12
    assert abs(row.correlation - 1) < 1e-12
