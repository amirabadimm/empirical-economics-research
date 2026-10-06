import pytest

from asset_allocation.collectors.tsetmc_reit_adjusted import parse_chart


def test_adjusted_chart_parser_uses_official_close_field():
    payload = b"20260930,100,90,95,98,12000,97;20261001,105,92,98,101,13000,100;"
    assert parse_chart(payload) == {"2026-09-30": 97.0, "2026-10-01": 100.0}


def test_adjusted_chart_rejects_duplicate_date():
    payload = b"20260930,100,90,95,98,12000,97;20260930,100,90,95,98,12000,97;"
    with pytest.raises(ValueError, match="duplicate"):
        parse_chart(payload)
