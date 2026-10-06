from datetime import date
from decimal import Decimal

import pytest

from asset_allocation.collectors import kilid_housing as housing


def test_live_snapshot_appends_only_complete_month_without_revising_history():
    old = housing.parse_snapshot(housing.ORIGINAL.read_bytes())
    assert Decimal(old["1403/05"]) == Decimal("866")
    assert Decimal(old["1405/05"]) == Decimal("2100")
    existing = {period: {"jalali_period": period, "avg_price_million_irr_per_m2": value,
                         "source_snapshot": "old.html", "source_url": housing.URL}
                for period, value in old.items()}
    incoming = {"1405/04": old["1405/04"], "1405/05": old["1405/05"],
                "1404/12": old["1404/12"], "1405/06": "2200", "1405/07": "2200"}
    merged = housing.merge(existing, incoming, housing.SNAPSHOTS / "new.html", date(2026, 10, 6))
    assert len(merged) == len(existing) + 1
    assert merged["1405/06"]["avg_price_million_irr_per_m2"] == "2200"
    assert "1405/07" not in merged
    assert housing.merge(merged, incoming, housing.SNAPSHOTS / "new.html", date(2026, 10, 6)) == merged
    assert Decimal(merged["1405/05"]["avg_price_million_irr_per_m2"]) == Decimal("2100")


def test_revised_historical_kilid_value_is_rejected():
    old = {period: {"jalali_period": period, "avg_price_million_irr_per_m2": "100",
                    "source_snapshot": "old.html", "source_url": housing.URL}
           for period in ("1405/03", "1405/04", "1405/05")}
    incoming = {"1405/03": "100", "1405/04": "101", "1405/05": "100", "1405/06": "110"}
    with pytest.raises(ValueError, match="revised historical month"):
        housing.merge(old, incoming, housing.SNAPSHOTS / "new.html", date(2026, 10, 6))
