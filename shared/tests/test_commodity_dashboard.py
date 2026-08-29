"""Network-free contracts for standardized commodity notebook dashboards."""

import pandas as pd

from shared.notebook_tools.commodity_dashboard import goods_type_counts, market_summary


def test_goods_counts_use_every_physical_record() -> None:
    physical = pd.DataFrame({"GoodsName": ["A3/12", "coil", "A3/12", None]})
    counts = goods_type_counts(physical)
    assert counts["record_count"].sum() == len(physical)
    assert counts.set_index("goods_name").loc["A3/12", "record_count"] == 2
    assert "<missing>" in set(counts["goods_name"])


def test_market_summary_keeps_physical_and_certificate_units_separate() -> None:
    physical = pd.DataFrame(
        {"Quantity": [0, 2, 3], "date": ["1405/01/01", "1405/01/02", "1405/01/02"]}
    )
    certificate = pd.DataFrame(
        {"TradesVolume": [0, 4], "PersianDate": ["1405/01/01", "1405/01/03"]}
    )
    summary = market_summary(physical, certificate)
    assert summary.loc["physical", "positive_trade_records"] == 2
    assert summary.loc["physical", "trading_days"] == 1
    assert summary.loc["certificate", "positive_trade_records"] == 1
