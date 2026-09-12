"""Collect and archive official TSETMC TEDPIX daily index observations."""

from __future__ import annotations

import csv
import hashlib
import json
import os
import tempfile
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import requests

PROJECT_ROOT = Path(__file__).resolve().parents[3]
RAW_DIR = PROJECT_ROOT / "data" / "raw" / "tse_total_index"
SNAPSHOT_DIR = RAW_DIR / "tsetmc_snapshots"
CSV_PATH = RAW_DIR / "tedpix_daily.csv"
INS_CODE = "32097828799138957"
API_URL = f"https://cdn.tsetmc.com/api/Index/GetIndexB2History/{INS_CODE}"
CSV_FIELDS = ("source_date_gregorian", "ins_code", "index_close", "index_open", "index_high", "source_retrieved_at_utc")


def request_payload(timeout_seconds: int = 60) -> bytes:
    response = requests.get(API_URL, headers={"User-Agent": "asset-allocation-research/0.1"}, timeout=timeout_seconds)
    response.raise_for_status()
    return response.content


def parse_records(payload: bytes, retrieved_at_utc: str) -> list[dict[str, str]]:
    decoded: Any = json.loads(payload.decode("utf-8"))
    observations = decoded.get("indexB2") if isinstance(decoded, dict) else None
    if not isinstance(observations, list) or not observations:
        raise ValueError("TSETMC index payload has no indexB2 observations")
    rows: dict[str, dict[str, str]] = {}
    for observation in observations:
        raw_date = str(observation.get("dEven", ""))
        if len(raw_date) != 8 or not raw_date.isdecimal():
            raise ValueError(f"Invalid TSETMC index date: {raw_date!r}")
        date = datetime.strptime(raw_date, "%Y%m%d").date().isoformat()
        row = {
            "source_date_gregorian": date,
            "ins_code": INS_CODE,
            "index_close": str(float(observation["xNivInuClMresIbs"])),
            "index_open": str(float(observation["xNivInuPbMresIbs"])),
            "index_high": str(float(observation["xNivInuPhMresIbs"])),
            "source_retrieved_at_utc": retrieved_at_utc,
        }
        if date in rows and rows[date] != row:
            raise ValueError(f"Conflicting duplicate index date: {date}")
        rows[date] = row
    return [rows[date] for date in sorted(rows)]


def collect() -> dict[str, str | int]:
    retrieved_at = datetime.now(UTC).isoformat()
    payload = request_payload()
    snapshot = archive_snapshot(payload)
    rows = parse_records(payload, retrieved_at)
    write_canonical_csv(rows)
    return {"records": len(rows), "first_date": rows[0]["source_date_gregorian"], "last_date": rows[-1]["source_date_gregorian"], "snapshot": str(snapshot), "csv": str(CSV_PATH)}


def archive_snapshot(payload: bytes) -> Path:
    SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)
    path = SNAPSHOT_DIR / f"{hashlib.sha256(payload).hexdigest()}.json"
    if not path.exists():
        with tempfile.NamedTemporaryFile("wb", delete=False, dir=SNAPSHOT_DIR, suffix=".tmp") as file:
            file.write(payload)
            temporary = Path(file.name)
        os.replace(temporary, path)
    return path


def write_canonical_csv(rows: list[dict[str, str]]) -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", delete=False, dir=RAW_DIR, suffix=".tmp") as file:
        writer = csv.DictWriter(file, fieldnames=CSV_FIELDS)
        writer.writeheader()
        writer.writerows(rows)
        temporary = Path(file.name)
    os.replace(temporary, CSV_PATH)


if __name__ == "__main__":
    print(json.dumps(collect(), ensure_ascii=False, indent=2))
