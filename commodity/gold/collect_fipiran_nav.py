"""Collect independent Fipiran historical redemption NAV for five gold ETFs."""
import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

PROJECT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT / "src"))
from gold.collectors.fund_history import fetch, persist

FUNDS = ("ayar", "tala", "kahroba", "ganj", "gohar")


def verify_identity(session, fund, cfg, archive):
    try:
        response = session.post(
            "https://www.fipiran.com/services/fund/fundcompare/",
            json={"regNos": [], "showMarketMakers": False}, timeout=20,
        )
        response.raise_for_status()
    except requests.RequestException:
        # A recently archived directory response can still verify the fixed
        # registration identity when the large live directory times out.
        candidates = sorted((PROJECT / "data/raw/funds").glob(
            "*/snapshots/fipiran_identity/[0-9a-f]*.json"))
        candidates = [path for path in candidates if not path.name.endswith(".metadata.json")]
        for path in reversed(candidates):
            data = path.read_bytes()
            if hashlib.sha256(data).hexdigest() != path.stem:
                continue
            entries = json.loads(data)["items"]
            if any(str(row.get("regNo")) == str(cfg["nav_reg_no"])
                   and row.get("groupId") == cfg["fipiran_group_id"]
                   and row.get("name") == cfg["nav_fund_name"] for row in entries):
                print(f"{fund}: identity verified from archived Fipiran directory {path}")
                return
        raise
    archive.mkdir(parents=True, exist_ok=True)
    digest = hashlib.sha256(response.content).hexdigest()
    snapshot = archive / f"{digest}.json"
    if not snapshot.exists():
        with snapshot.open("xb") as handle:
            handle.write(response.content)
    metadata = archive / f"{digest}.metadata.json"
    if not metadata.exists():
        with metadata.open("x", encoding="utf-8") as handle:
            json.dump({"url": response.url, "method": "POST",
                       "retrieved_at_utc": datetime.now(timezone.utc).isoformat(),
                       "sha256": digest, "tls_verified": True}, handle)
    matches = [row for row in response.json()["items"]
               if str(row.get("regNo")) == str(cfg["nav_reg_no"])
               and row.get("groupId") == cfg["fipiran_group_id"]]
    if len(matches) != 1 or matches[0].get("name") != cfg["nav_fund_name"]:
        raise ValueError(f"{fund}: Fipiran identity mismatch: {matches!r}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fund", choices=FUNDS)
    parser.add_argument("--full", action="store_true",
                        help="Fetch complete history for initial load or older revisions")
    args = parser.parse_args()
    configs = json.loads((PROJECT / "config/funds.json").read_text(encoding="utf-8"))
    session = requests.Session()
    session.headers.update({"User-Agent": "Mozilla/5.0", "Referer": "https://www.fipiran.com/"})
    session.mount("https://", HTTPAdapter(max_retries=Retry(
        total=3, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504]
    )))
    for fund in ([args.fund] if args.fund else FUNDS):
        cfg = configs[fund]
        raw = PROJECT / "data/raw/funds" / fund
        canonical = raw / "nav_fipiran.csv"
        full = args.full or not canonical.exists()
        verify_identity(session, fund, cfg, raw / "snapshots/fipiran_identity")
        payload, digest = fetch(
            session, "https://www.fipiran.com/services/chart/getfundchart",
            raw / "snapshots/fipiran_nav",
            {"regno": cfg["nav_reg_no"], "groupId": cfg["fipiran_group_id"],
             "showAll": str(full).lower()},
        )
        if not isinstance(payload, list) or not payload:
            raise ValueError(f"{fund}: empty Fipiran NAV history")
        frame = pd.DataFrame([
            {"date": row["date"][:10], "redemption_nav_irr": row["cancelNav"],
             "issuance_nav_irr": row["issueNav"],
             "statistical_nav_irr": row["statisticalNav"],
             "source_snapshot": digest}
            for row in payload
        ])
        numbers = frame[["redemption_nav_irr", "issuance_nav_irr", "statistical_nav_irr"]]
        if not np.isfinite(numbers.to_numpy(dtype=float)).all() or (numbers <= 0).any().any():
            raise ValueError(f"{fund}: invalid NAV")
        unique = frame.groupby("date")[["redemption_nav_irr", "issuance_nav_irr",
                                         "statistical_nav_irr"]].nunique()
        if (unique > 1).any().any():
            raise ValueError(f"{fund}: conflicting NAVs on one Fipiran date")
        frame = frame.drop_duplicates("date")
        if not full:
            last_saved = pd.read_csv(canonical, usecols=["date"]).date.max()
            if not frame.date.min() <= last_saved <= frame.date.max():
                raise ValueError(f"{fund}: recent response does not cover the last saved date; run --full")
        persist(frame, canonical)
        print(f"{fund}: {len(frame)} {'full' if full else 'recent'} Fipiran NAV dates, "
              f"{frame.date.min()} through {frame.date.max()}")


if __name__ == "__main__":
    main()
