from datetime import date

import pandas as pd

from asset_allocation import build_housing_two_year_cumulative as housing


def test_housing_uses_month_ends_and_stops_at_last_observation(tmp_path, monkeypatch):
    source = tmp_path / "monthly_asset_levels.csv"
    pd.DataFrame([
        {"jalali_period": "1403/06", "asset_id": "tehran_housing", "month_end_level": 90,
         "source_method": "source", "data_quality_flag": "ok"},
        {"jalali_period": "1403/07", "asset_id": "tehran_housing", "month_end_level": 100,
         "source_method": "source", "data_quality_flag": "ok"},
        {"jalali_period": "1403/08", "asset_id": "tehran_housing", "month_end_level": 110,
         "source_method": "source", "data_quality_flag": "ok"},
        {"jalali_period": "1405/05", "asset_id": "tehran_housing", "month_end_level": 200,
         "source_method": "source", "data_quality_flag": "proxy"},
    ]).to_csv(source, index=False)
    monkeypatch.setattr(housing, "atomic_frame", lambda path, frame: None)
    panel, summary = housing.build(date(2026, 10, 2), source)
    assert len(panel) == 3
    assert panel.observation_date_gregorian.iloc[0] == "2024-10-21"
    assert panel.observation_date_gregorian.iloc[-1] == "2026-08-22"
    assert panel.cumulative_return.iloc[0] == 0
    assert panel.cumulative_return.iloc[-1] == 1
    assert summary.observed_months.iloc[0] == 3
    assert summary.latest_observation_date.iloc[0] == "2026-08-22"
