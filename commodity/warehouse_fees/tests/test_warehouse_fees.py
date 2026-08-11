from pathlib import Path
from datetime import date
import csv

from commodity.warehouse_fees.src.warehouse_fees.build_daily import OUTPUT_COLUMNS, build


def test_final_daily_panel():
    project = Path(__file__).resolve().parents[1]
    output = build(project, through=date(2026, 8, 11))
    with output.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        rows = list(reader)
        assert reader.fieldnames == OUTPUT_COLUMNS
    indexed = {(row["date"], row["commodity"]): row for row in rows}
    assert len(indexed) == len(rows)
    assert indexed[("2025-10-20", "bitumen_60_70")]["daily_storage_fee_rial"] == "0"
    assert indexed[("2026-04-10", "iron_ore_pellet")]["daily_storage_fee_rial"] == "2"
    assert indexed[("2026-04-11", "iron_ore_pellet")]["daily_storage_fee_rial"] == "3"
    assert indexed[("2026-08-11", "iron_ore_pellet")]["assessment_fee_rial"] == "0"
    assert len({row["commodity"] for row in rows}) == 21
    assert min(row["date"] for row in rows) == "2016-10-29"


def test_historical_observations_are_unique():
    project = Path(__file__).resolve().parents[1]
    path = project / "data" / "interim" / "historical_page_observations.csv"
    with path.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) == 30
    keys = {(row["observed_at"], row["commodity"]) for row in rows}
    assert len(keys) == len(rows)
    assert min(row["observed_at"] for row in rows) == "2016-10-29"
