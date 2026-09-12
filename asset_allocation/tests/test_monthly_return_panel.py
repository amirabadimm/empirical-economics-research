import csv
import math
from decimal import Decimal

from asset_allocation.build_monthly_return_panel import (
    ASSETS,
    HOUSING_OVERRIDES_PATH,
    LEVELS_PATH,
    RETURNS_PATH,
    build,
    periods,
)
from asset_allocation.audit_housing import AUDIT_OUTPUT_PATH, audit_workbook


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

    corrected = {
        row["jalali_period"]: row
        for row in levels
        if row["asset_id"] == "tehran_housing"
    }
    assert Decimal(corrected["1396/12"]["month_end_level"]) == Decimal("57.591")
    assert Decimal(corrected["1397/01"]["month_end_level"]) == Decimal("55.280")
    assert Decimal(corrected["1397/04"]["month_end_level"]) == Decimal("69.728")
    assert Decimal(corrected["1397/07"]["month_end_level"]) == Decimal("86.109")
    assert Decimal(corrected["1397/07"]["raw_source_level"]) == Decimal("0.6811")
    assert corrected["1397/07"]["source_report"].endswith("9707.pdf")
    assert corrected["1397/07"]["source_method"] == "CBI_source_adjudicated_override"

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


def test_housing_integrity_and_diagnostic_report() -> None:
    build()
    with LEVELS_PATH.open(encoding="utf-8-sig", newline="") as source:
        housing = [
            row for row in csv.DictReader(source) if row["asset_id"] == "tehran_housing"
        ]
    assert len({row["jalali_period"] for row in housing}) == len(housing)
    assert [row["jalali_period"] for row in housing] == sorted(
        row["jalali_period"] for row in housing
    )
    assert all(row["unit"] == "million_IRR_per_m2" for row in housing)
    assert all(Decimal(row["month_end_level"]) > 0 for row in housing if row["month_end_level"])

    official = [
        row
        for row in housing
        if row["jalali_period"] <= "1403/05" and row["month_end_level"]
    ]
    values = [Decimal(row["month_end_level"]) for row in official]
    for previous, current in zip(values, values[1:]):
        ratio = current / previous
        assert Decimal("0.2") <= ratio <= Decimal("5")

    with AUDIT_OUTPUT_PATH.open(encoding="utf-8-sig", newline="") as source:
        audit_rows = list(csv.DictReader(source))
    assert len(audit_rows) == 101
    assert len({row["jalali_period"] for row in audit_rows}) == 101
    assert all(row["source_pdf"] and row["provenance_method"] for row in audit_rows)
    assert all(not row["diagnostic_flag"] for row in audit_rows)


def test_housing_returns_are_finite_and_corrected_sequence_reconciles() -> None:
    build()
    with RETURNS_PATH.open(encoding="utf-8-sig", newline="") as source:
        housing = {
            row["jalali_period"]: row
            for row in csv.DictReader(source)
            if row["asset_id"] == "tehran_housing"
        }
    for row in housing.values():
        if row["monthly_return"]:
            assert math.isfinite(float(row["monthly_return"]))
        else:
            assert row["missing_reason"]
            assert row["monthly_return"] != "0"
    expected = {
        "1397/06": Decimal("80.958") / Decimal("73.999") - 1,
        "1397/07": Decimal("86.109") / Decimal("80.958") - 1,
        "1397/08": Decimal("91.794") / Decimal("86.109") - 1,
    }
    for period, value in expected.items():
        assert Decimal(housing[period]["monthly_return"]) == value.quantize(
            Decimal("0.000000000001")
        )


def test_raw_workbook_audit_detects_original_mehr_corruption() -> None:
    audit = audit_workbook()
    assert ("1397/07", 0.6811, [80.958, 91.794]) in audit["order_of_magnitude_flags"]


def test_source_adjudications_preserve_adjacent_report_evidence() -> None:
    with HOUSING_OVERRIDES_PATH.open(encoding="utf-8-sig", newline="") as source:
        rows = {row["jalali_period"]: row for row in csv.DictReader(source)}
    for period in ("1397/01", "1397/04", "1397/07"):
        row = rows[period]
        assert row["primary_source_pdf"].endswith(".pdf")
        assert row["verification_source_pdf"].endswith(".pdf")
        assert row["primary_evidence"]
        assert row["verification_evidence"]
        assert row["quality_flag"] == "corrected_adjacent_official_reports_agree"
    assert rows["1396/12"]["quality_flag"].endswith("revision_disagreement")
    assert rows["1398/08"]["original_extracted_value_million_irr_m2"] == rows[
        "1398/08"
    ]["corrected_value_million_irr_m2"]
