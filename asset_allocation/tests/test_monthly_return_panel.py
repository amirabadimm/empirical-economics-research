import csv
from decimal import Decimal

from asset_allocation.build_monthly_return_panel import (
    ASSETS,
    LEVELS_PATH,
    RETURNS_PATH,
    build,
    periods,
)


def test_panel_has_complete_month_asset_grid_and_no_filled_missing_returns() -> None:
    result = build()
    assert result["level_rows"] == 126 * 4
    assert result["return_rows"] == 125 * 4
    with LEVELS_PATH.open(encoding="utf-8-sig", newline="") as source:
        levels = list(csv.DictReader(source))
    with RETURNS_PATH.open(encoding="utf-8-sig", newline="") as source:
        returns = list(csv.DictReader(source))
    assert {(row["jalali_period"], row["asset_id"]) for row in levels} == {
        (period, asset) for period in periods("1394/12", "1405/05") for asset in ASSETS
    }
    assert {(row["jalali_period"], row["asset_id"]) for row in returns} == {
        (period, asset) for period in periods("1395/01", "1405/05") for asset in ASSETS
    }
    housing_first = next(row for row in returns
                         if row["jalali_period"] == "1395/01" and row["asset_id"] == "tehran_housing")
    assert housing_first["monthly_return"] == ""
    assert housing_first["missing_reason"] == "missing_previous_month_level"
    assert all(row["monthly_return"] != "0" for row in returns if row["missing_reason"])
    housing_kilid = next(row for row in levels
                         if row["jalali_period"] == "1403/06" and row["asset_id"] == "tehran_housing")
    assert housing_kilid["source_method"] == "Kilid_chain_linked_to_CBI_1403_05"
    assert housing_kilid["data_quality_flag"] == "secondary_proxy_low_overlap_similarity"
    assert Decimal(housing_kilid["link_factor"]) == Decimal("1.021939953811")

    housing_returns = [row for row in returns if row["asset_id"] == "tehran_housing"]
    assert sum(bool(row["monthly_return"]) for row in housing_returns) == 124
    assert all(row["monthly_return"] for row in housing_returns[1:])


def test_returns_reconcile_to_adjacent_month_end_levels() -> None:
    build()
    with RETURNS_PATH.open(encoding="utf-8-sig", newline="") as source:
        returns = list(csv.DictReader(source))
    for row in returns:
        if not row["monthly_return"]:
            continue
        expected = Decimal(row["current_month_end_level"]) / Decimal(row["previous_month_end_level"]) - 1
        assert Decimal(row["monthly_return"]) == expected.quantize(Decimal("0.000000000001"))
