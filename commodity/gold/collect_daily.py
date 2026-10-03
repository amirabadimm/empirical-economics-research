"""Collect daily trading history and historical redemption NAV for configured ETFs.

Only collectors write canonical raw CSVs. Responses are archived before parsing.
"""
import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

PROJECT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT / "src"))
from gold.collectors.fund_history import fetch, persist

ACTIVE_FUNDS = ("ayar", "tala", "kahroba", "ganj", "gohar")


def collect_price(session, fund, cfg, full=False):
    raw = PROJECT / "data/raw/funds" / fund
    canonical = raw / "price.csv"
    full = full or not canonical.exists()
    payload, digest = fetch(
        session,
        f"https://cdn.tsetmc.com/api/ClosingPrice/GetClosingPriceDailyList/{cfg['ins_code']}/{0 if full else 30}",
        raw / "snapshots/tsetmc",
    )
    rows = payload["closingPriceDaily"]
    if not rows:
        raise ValueError(f"{fund}: empty price history")
    frame = pd.DataFrame([
        {
            "date": datetime.strptime(str(row["dEven"]), "%Y%m%d").date().isoformat(),
            "ins_code": cfg["ins_code"],
            "closing_price_irr": row["pClosing"],
            "last_price_irr": row["pDrCotVal"],
            "trade_volume": row["qTotTran5J"],
            "trade_count": row["zTotTran"],
            "source_snapshot": digest,
        }
        for row in rows
    ])
    numbers = frame[["closing_price_irr", "last_price_irr", "trade_volume", "trade_count"]]
    if not np.isfinite(numbers.to_numpy(dtype=float)).all() or (numbers < 0).any().any():
        raise ValueError(f"{fund}: invalid price or activity")
    if not full:
        last_saved = pd.read_csv(canonical, usecols=["date"]).date.max()
        if not frame.date.min() <= last_saved <= frame.date.max():
            raise ValueError(f"{fund}: recent price response does not cover the last saved date; run --full")
    persist(frame, canonical)
    return len(frame)


def collect_nav(session, fund, cfg):
    if cfg.get("nav_provider") != "tsetmc_fund_detail":
        return None
    raw = PROJECT / "data/raw/funds" / fund
    payload, digest = fetch(
        session,
        f"https://cdn.tsetmc.com/api/Fund/GetFundInDetail/{cfg['nav_reg_no']}",
        raw / "snapshots/tsetmc_nav",
    )
    detail = payload["fund"]
    if detail.get("mfName") != cfg["nav_fund_name"]:
        raise ValueError(f"{fund}: NAV fund identity mismatch: {detail.get('mfName')!r}")
    rows = detail.get("stats") or []
    if not rows:
        raise ValueError(f"{fund}: empty redemption NAV history")
    frame = pd.DataFrame([
        {
            "date": row["recordDate"][:10],
            "redemption_nav_irr": row["navRed"],
            "issuance_nav_irr": row["navSub"],
            "statistical_nav_irr": row["navStat"],
            "source_snapshot": digest,
        }
        for row in rows
    ])
    numbers = frame[["redemption_nav_irr", "issuance_nav_irr", "statistical_nav_irr"]]
    if not np.isfinite(numbers.to_numpy(dtype=float)).all() or (numbers <= 0).any().any():
        raise ValueError(f"{fund}: invalid NAV")
    conflicting = frame.groupby("date")[["redemption_nav_irr", "issuance_nav_irr",
                                         "statistical_nav_irr"]].nunique()
    if (conflicting > 1).any().any():
        raise ValueError(f"{fund}: conflicting NAVs on the same source date")
    frame = frame.drop_duplicates("date")
    persist(frame, raw / ("nav_tsetmc.csv" if fund == "ayar" else "nav.csv"))
    return len(frame)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fund", choices=(*ACTIVE_FUNDS, "mesghal"))
    parser.add_argument("--full", action="store_true",
                        help="Fetch complete price history for initial load or older revisions")
    parser.add_argument("--comparison-nav", action="store_true",
                        help="Also collect complete TSETMC fund-detail NAV for comparison")
    args = parser.parse_args()
    configs = json.loads((PROJECT / "config/funds.json").read_text(encoding="utf-8"))
    session = requests.Session()
    session.mount("https://", HTTPAdapter(max_retries=Retry(
        total=3, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504]
    )))
    for fund in ([args.fund] if args.fund else ACTIVE_FUNDS):
        cfg = configs[fund]
        prices = collect_price(session, fund, cfg, full=args.full)
        nav = collect_nav(session, fund, cfg) if args.comparison_nav else None
        nav_status = (f"{nav} source NAV dates" if nav is not None else
                      "comparison NAV skipped")
        print(f"{fund}: {prices} source price rows; {nav_status}")


if __name__ == "__main__":
    main()
