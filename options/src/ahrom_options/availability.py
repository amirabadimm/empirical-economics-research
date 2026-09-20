from __future__ import annotations

import csv
import json
from datetime import datetime
from pathlib import Path

from .common import ROOT, archive_json, atomic_bytes, atomic_csv, fetch_json, read_archive, session
from .discover_contracts import MASTER_COLUMNS

BASE = "https://cdn.tsetmc.com/api/ClosingPrice/GetClosingPriceDailyList/"


def apply_dates(contract: dict, body: dict) -> None:
    records = body.get("closingPriceDaily")
    if not isinstance(records, list):
        raise ValueError("closingPriceDaily is not a list")
    code = contract["ins_code"]
    dates = [datetime.strptime(str(row["dEven"]), "%Y%m%d").date().isoformat()
             for row in records if str(row.get("insCode")) == code]
    if len(dates) != len(records):
        raise ValueError("TSETMC daily history includes another InsCode or missing dates")
    if dates:
        contract["first_available_date"] = min(dates)
        contract["last_available_date"] = max(dates)


def enrich(root: Path = ROOT, *, delay: float = 0.25, refresh: bool = False) -> dict:
    master = root / "data/processed/ahrom_option_contracts.csv"
    with master.open(encoding="utf-8-sig", newline="") as source:
        contracts = list(csv.DictReader(source))
    client = session()
    failures = []
    archives = {}
    attempted = 0
    for index, contract in enumerate(contracts, 1):
        code = contract["ins_code"]
        directory = root / "data/raw/tsetmc/daily" / code
        prior_archives = list(directory.glob("*.json")) if directory.exists() else []
        if prior_archives and not refresh:
            cached = max(prior_archives, key=lambda path: path.stat().st_mtime)
            try:
                apply_dates(contract, read_archive(cached))
                archives[code] = str(cached.relative_to(root))
                continue
            except (OSError, ValueError, KeyError, TypeError):
                pass
        attempted += 1
        try:
            body = fetch_json(client, BASE + code + "/0", delay=delay)
            archive = archive_json(directory, body)
            archives[code] = str(archive.relative_to(root))
            apply_dates(contract, body)
        except Exception as exc:
            failures.append({"ins_code": code, "error_type": type(exc).__name__,
                             "message": str(exc)[:200]})
        if index % 25 == 0:
            atomic_csv(master, contracts, MASTER_COLUMNS)
            print(f"TSETMC availability checked: {index}/{len(contracts)}", flush=True)
    atomic_csv(master, contracts, MASTER_COLUMNS)
    audit = {"checked": len(contracts), "attempted_this_run": attempted,
             "with_dates": sum(bool(c["first_available_date"]) for c in contracts),
             "archives": archives, "failures": failures}
    atomic_bytes(root / "data/processed/availability_audit.json",
                 json.dumps(audit, ensure_ascii=False, indent=2).encode())
    return audit
