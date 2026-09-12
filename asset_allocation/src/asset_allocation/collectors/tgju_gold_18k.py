"""Collect TGJU's public 18-karat gold daily history through its API."""

from __future__ import annotations

import csv
import hashlib
import json
import os
import re
import tempfile
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import requests

PROJECT_ROOT = Path(__file__).resolve().parents[3]
RAW_DIR = PROJECT_ROOT / "data" / "raw" / "gold_18k"
SNAPSHOT_DIR = RAW_DIR / "tgju_snapshots"
CSV_PATH = RAW_DIR / "tgju_gold_18k_daily.csv"
API_URL = "https://api.tgju.org/v1/market/indicator/summary-table-data/geram18?lang=fa&order_dir=asc"
CSV_FIELDS = (
    "source_date_gregorian",
    "source_date_jalali",
    "price_open_irr_per_gram",
    "price_low_irr_per_gram",
    "price_high_irr_per_gram",
    "price_close_irr_per_gram",
    "source_retrieved_at_utc",
)


def request_payload(timeout_seconds: int = 60) -> bytes:
    response = requests.get(API_URL, headers={"User-Agent": "asset-allocation-research/0.1"}, timeout=timeout_seconds)
    response.raise_for_status()
    return response.content


def _number(value: Any) -> str:
    cleaned = re.sub(r"[^0-9.]", "", str(value))
    if not cleaned:
        raise ValueError(f"TGJU value is not numeric: {value!r}")
    return str(float(cleaned))


def parse_records(payload: bytes, retrieved_at_utc: str) -> list[dict[str, str]]:
    decoded: Any = json.loads(payload.decode("utf-8"))
    observations = decoded.get("data") if isinstance(decoded, dict) else None
    if not isinstance(observations, list) or not observations:
        raise ValueError("TGJU 18-karat gold payload has no observations")
    rows: dict[str, dict[str, str]] = {}
    for observation in observations:
        if not isinstance(observation, list) or len(observation) < 8:
            raise ValueError(f"Malformed TGJU 18-karat gold observation: {observation!r}")
        gregorian_date = str(observation[6]).replace("/", "-")
        datetime.strptime(gregorian_date, "%Y-%m-%d")
        row = {
            "source_date_gregorian": gregorian_date,
            "source_date_jalali": str(observation[7]).replace("/", "-"),
            "price_open_irr_per_gram": _number(observation[0]),
            "price_low_irr_per_gram": _number(observation[1]),
            "price_high_irr_per_gram": _number(observation[2]),
            "price_close_irr_per_gram": _number(observation[3]),
            "source_retrieved_at_utc": retrieved_at_utc,
        }
        if gregorian_date in rows and rows[gregorian_date] != row:
            raise ValueError(f"Conflicting duplicate TGJU gold date: {gregorian_date}")
        rows[gregorian_date] = row
    return [rows[date] for date in sorted(rows)]


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


def collect() -> dict[str, str | int]:
    retrieved_at = datetime.now(UTC).isoformat()
    payload = request_payload()
    snapshot = archive_snapshot(payload)
    rows = parse_records(payload, retrieved_at)
    write_canonical_csv(rows)
    return {"records": len(rows), "first_date": rows[0]["source_date_gregorian"], "last_date": rows[-1]["source_date_gregorian"], "snapshot": str(snapshot), "csv": str(CSV_PATH)}


if __name__ == "__main__":
    print(json.dumps(collect(), ensure_ascii=False, indent=2))
