import csv
from datetime import date

import pandas as pd

from asset_allocation import build_reit_two_year_cumulative as cumulative


def test_rebases_later_fund_from_its_first_observed_week(tmp_path, monkeypatch):
    manifest = tmp_path / "instruments.csv"
    with manifest.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=["ins_code"])
        writer.writeheader()
        writer.writerow({"ins_code": "1"})
    monkeypatch.setattr(cumulative, "MANIFEST", manifest)
    monkeypatch.setattr(cumulative, "ENGLISH_NAMES", {"1": "New Fund"})
    monkeypatch.setattr(cumulative, "FUNDS", {"1": "New Fund"})
    monkeypatch.setattr(cumulative, "atomic_frame", lambda path, frame: None)

    def closes(path, field, earliest, anchor, traded_only=False):
        return {date(2024, 10, 4): {"index_close": "100", "source_date_gregorian": "2024-10-02"},
                date(2026, 10, 2): {"index_close": "150", "source_date_gregorian": "2026-10-01"}}

    monkeypatch.setattr(cumulative, "weekly_closes", closes)
    monkeypatch.setattr(cumulative, "reinvested_weekly_closes", lambda path, code, cutoff, anchor: {
        date(2026, 9, 25): (200, "2026-09-24", "assembly_date_reinvested_traded_close"),
        date(2026, 10, 2): (220, "2026-10-01", "assembly_date_reinvested_traded_close"),
    })
    monkeypatch.setattr(cumulative, "usd_weekly_closes", lambda path, earliest, anchor: {
        date(2024, 10, 4): {"price": 1000, "observed": date(2024, 10, 2), "method": "legacy_high_low_midpoint"},
        date(2026, 10, 2): {"price": 2000, "observed": date(2026, 10, 1), "method": "close"},
    })
    panel, summary = cumulative.build(date(2026, 10, 2))
    by_asset = summary.set_index("asset")
    assert by_asset.loc["TEDPIX", "cumulative_return"] == 0.5
    assert by_asset.loc["USD/IRR", "cumulative_return"] == 1.0
    assert by_asset.loc["New Fund", "baseline_week_end"] == "2026-09-25"
    assert abs(by_asset.loc["New Fund", "cumulative_return"] - 0.1) < 1e-12
    early_fund = panel.loc[(panel.asset == "New Fund") & (panel.week_end_gregorian == "2024-10-04")]
    assert pd.isna(early_fund.cumulative_return.iloc[0])
    assert panel.loc[panel.asset == "New Fund", "return_definition"].eq("assembly_date_cash_reinvested_traded_close_scenario").all()
