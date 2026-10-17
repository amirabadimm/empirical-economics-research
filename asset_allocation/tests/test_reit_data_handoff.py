from datetime import date, timedelta

import pandas as pd

from asset_allocation.build_reit_data_handoff import POST_WAR_START, trading_value_archive, window_return
from asset_allocation.build_reit_assembly_reinvestment import FUNDS, RAW
from asset_allocation.build_reit_subscription_facts import build as build_subscriptions


def test_post_war_cutoff_counts_forty_inclusive_days():
    assert POST_WAR_START == date(2026, 2, 28) + timedelta(days=40)
    assert POST_WAR_START.isoformat() == "2026-04-09"


def test_trading_value_snapshots_cover_every_raw_fund_date():
    archive = trading_value_archive()
    assert len(archive) == 4057
    for code in FUNDS:
        raw = pd.read_csv(RAW / f"{code}.csv", dtype={"ins_code": str})
        for row in raw.itertuples():
            source = archive[(code, row.source_date_gregorian)]
            assert source["snapshot_close"] == row.closing_price_irr
            assert source["trading_value_irr"] >= 0


def test_post_war_uses_first_actual_trade_after_suspension():
    frame = pd.DataFrame({
        "source_date_gregorian": ["2026-02-26", "2026-05-02", "2026-05-06"],
        "traded_close_irr": [100, 80, 100],
    })
    baseline, result = window_return(frame, POST_WAR_START, "traded_close_irr", max_gap_days=None)
    assert baseline == "2026-05-02"
    assert result == 0.25


def test_subscription_public_proceeds_match_archived_exchange_trades():
    facts = build_subscriptions().set_index("fund")
    assert facts.loc["Kelid", "initial_public_subscription_units"] == 452593307
    assert facts.loc["Amin Shahr", "subscription_proceeds_billion_toman"] == 352.537003
    assert facts.loc["Kakh", "initial_public_subscription_units"] == 690002547
    assert len(facts) == 8
