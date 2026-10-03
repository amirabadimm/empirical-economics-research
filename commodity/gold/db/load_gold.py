"""Load the five canonical gold ETF histories into PostgreSQL atomically.

The source CSVs remain the canonical raw files. This program only reads them.
Set GOLD_DATABASE_URL in the environment; credentials are never command arguments.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import sys
from pathlib import Path

import pandas as pd

PROJECT = Path(__file__).resolve().parents[1]
ROOT = PROJECT.parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(PROJECT / "src"))

from gold.processing.build_nav_bubble import calculate
from shared.market_analysis.bubble_percentiles import expanding_percentiles

FUNDS = ("ayar", "tala", "kahroba", "ganj", "gohar")
METHOD = "exact_date_close_fipiran_redemption_v1"
PROVIDER = "fipiran_historical"


def _read(path: Path, required: set[str]) -> pd.DataFrame:
    frame = pd.read_csv(path, dtype={"source_snapshot": "string"})
    missing = required - set(frame.columns)
    if missing:
        raise ValueError(f"{path}: missing columns {sorted(missing)}")
    frame["date"] = pd.to_datetime(frame["date"], errors="raise")
    if frame.date.isna().any() or frame.date.duplicated().any():
        raise ValueError(f"{path}: missing or duplicate dates")
    hashes = frame.source_snapshot.fillna("")
    if not hashes.str.fullmatch(r"[0-9a-f]{64}").all():
        raise ValueError(f"{path}: missing or invalid source snapshot hash")
    return frame.sort_values("date").reset_index(drop=True)


def decile_from_percentile(percentile: pd.Series) -> pd.Series:
    """Map inclusive historical ranks to deciles (0,10] ... (90,100]."""
    return percentile.round(8).div(10).apply(math.ceil).clip(1, 10).astype(int)


def prepare_fund(fund: str, cfg: dict, source_dir: Path = PROJECT / "data/raw/funds"):
    raw = source_dir / fund
    prices = _read(raw / "price.csv", {
        "date", "ins_code", "closing_price_irr", "last_price_irr",
        "trade_volume", "trade_count", "source_snapshot",
    })
    nav = _read(raw / "nav_fipiran.csv", {
        "date", "redemption_nav_irr", "issuance_nav_irr",
        "statistical_nav_irr", "source_snapshot",
    })
    if not prices.ins_code.astype(str).eq(str(cfg["ins_code"])).all():
        raise ValueError(f"{fund}: price InsCode differs from configured instrument")
    for name, frame, columns in (
        ("price", prices, ("closing_price_irr", "last_price_irr", "trade_volume", "trade_count")),
        ("NAV", nav, ("redemption_nav_irr",)),
    ):
        for column in columns:
            frame[column] = pd.to_numeric(frame[column], errors="raise")
            if not frame[column].map(math.isfinite).all() or (frame[column] < 0).any():
                raise ValueError(f"{fund}: invalid {name} {column}")
    if (nav.redemption_nav_irr <= 0).any():
        raise ValueError(f"{fund}: nonpositive redemption NAV")
    if not prices.trade_count.mod(1).eq(0).all():
        raise ValueError(f"{fund}: noninteger trade count")

    bubbles = calculate(prices, nav)
    ranks = expanding_percentiles(
        bubbles[["date", "bubble_pct"]].rename(columns={"date": "observation_date"}),
        half_life_days=float(cfg["half_life_days"]),
    )
    bubbles = bubbles.merge(ranks[[
        "observation_date", "expanding_percentile", "recent_weighted_percentile", "history_count",
    ]], left_on="date", right_on="observation_date", validate="one_to_one")
    # The inclusive percentile counts all historical bubbles <= today's value.
    # Decile 1 is (0, 10], and decile 10 is (90, 100].
    bubbles["expanding_decile"] = decile_from_percentile(bubbles.expanding_percentile)
    return prices, nav, bubbles


def load_fund(cur, fund: str, cfg: dict, prepared) -> tuple[int, int, int]:
    prices, nav, bubbles = prepared
    cur.execute("""
        INSERT INTO research.instruments
            (asset_class, instrument_key, display_name, exchange_code, currency_code, unit_label)
        VALUES ('gold_etf', %s, %s, %s, 'IRR', 'per fund unit')
        ON CONFLICT (instrument_key) DO UPDATE SET
            display_name = EXCLUDED.display_name, exchange_code = EXCLUDED.exchange_code
        RETURNING instrument_id
    """, (fund, cfg["name"], str(cfg["ins_code"])))
    instrument_id = cur.fetchone()[0]
    price_rows = [(
        instrument_id, row.date.date(), row.closing_price_irr, row.last_price_irr,
        row.trade_volume, int(row.trade_count), "tsetmc", row.source_snapshot,
    ) for row in prices.itertuples(index=False)]
    nav_rows = [(
        instrument_id, row.date.date(), PROVIDER, row.redemption_nav_irr,
        None if pd.isna(row.issuance_nav_irr) else row.issuance_nav_irr,
        None if pd.isna(row.statistical_nav_irr) else row.statistical_nav_irr,
        row.source_snapshot,
    ) for row in nav.itertuples(index=False)]
    cur.executemany("""
        INSERT INTO research.daily_prices
            (instrument_id, observation_date, close_irr, last_irr, trade_volume,
             trade_count, source_name, source_snapshot_sha256)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (instrument_id, observation_date) DO UPDATE SET
            close_irr = EXCLUDED.close_irr, last_irr = EXCLUDED.last_irr,
            trade_volume = EXCLUDED.trade_volume, trade_count = EXCLUDED.trade_count,
            source_name = EXCLUDED.source_name,
            source_snapshot_sha256 = EXCLUDED.source_snapshot_sha256,
            loaded_at = now()
        WHERE (daily_prices.close_irr, daily_prices.last_irr, daily_prices.trade_volume,
               daily_prices.trade_count, daily_prices.source_name,
               daily_prices.source_snapshot_sha256) IS DISTINCT FROM
              (EXCLUDED.close_irr, EXCLUDED.last_irr, EXCLUDED.trade_volume,
               EXCLUDED.trade_count, EXCLUDED.source_name, EXCLUDED.source_snapshot_sha256)
    """, price_rows)
    cur.executemany("""
        INSERT INTO research.daily_nav
            (instrument_id, observation_date, provider_key, redemption_irr,
             issuance_irr, statistical_irr, source_snapshot_sha256)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (instrument_id, observation_date, provider_key) DO UPDATE SET
            redemption_irr = EXCLUDED.redemption_irr,
            issuance_irr = EXCLUDED.issuance_irr,
            statistical_irr = EXCLUDED.statistical_irr,
            source_snapshot_sha256 = EXCLUDED.source_snapshot_sha256,
            loaded_at = now()
        WHERE (daily_nav.redemption_irr, daily_nav.issuance_irr,
               daily_nav.statistical_irr, daily_nav.source_snapshot_sha256)
          IS DISTINCT FROM
              (EXCLUDED.redemption_irr, EXCLUDED.issuance_irr,
               EXCLUDED.statistical_irr, EXCLUDED.source_snapshot_sha256)
    """, nav_rows)
    # Bubble rows are derived. Replace this method's series within the same transaction.
    cur.execute("""
        DELETE FROM research.bubble_observations
        WHERE instrument_id = %s AND method_key = %s
    """, (instrument_id, METHOD))
    bubble_rows = [(
        instrument_id, row.date.date(), METHOD, PROVIDER, row.bubble_pct,
        row.spread_irr, row.expanding_percentile, int(row.expanding_decile),
        row.recent_weighted_percentile, int(row.history_count), cfg["half_life_days"],
    ) for row in bubbles.itertuples(index=False)]
    cur.executemany("""
        INSERT INTO research.bubble_observations
            (instrument_id, observation_date, method_key, nav_provider_key,
             bubble_pct, spread_irr, expanding_percentile, expanding_decile,
             recent_weighted_percentile, history_count, half_life_days)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, bubble_rows)
    return len(price_rows), len(nav_rows), len(bubble_rows)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fund", choices=FUNDS, help="Load one fund; default is all five")
    parser.add_argument("--source-dir", type=Path, default=PROJECT / "data/raw/funds")
    args = parser.parse_args()
    funds = (args.fund,) if args.fund else FUNDS
    configs = json.loads((PROJECT / "config/funds.json").read_text(encoding="utf-8"))
    prepared = {fund: prepare_fund(fund, configs[fund], args.source_dir) for fund in funds}
    url = os.environ.get("GOLD_DATABASE_URL")
    if not url:
        raise SystemExit("Set GOLD_DATABASE_URL in the environment")
    try:
        import psycopg
    except ImportError as exc:
        raise SystemExit("Install the database extra: pip install -e '.[database]'") from exc
    with psycopg.connect(url) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT pg_advisory_xact_lock(hashtext('gold_etf_loader_v1'))")
            for fund in funds:
                counts = load_fund(cur, fund, configs[fund], prepared[fund])
                print(f"{fund}: {counts[0]} prices, {counts[1]} NAVs, {counts[2]} bubbles")
    print("Committed database load")


if __name__ == "__main__":
    main()
