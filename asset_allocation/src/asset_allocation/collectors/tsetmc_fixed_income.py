"""Collect and archive TSETMC daily closing prices for the selected ETF."""

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
RAW_DIR = PROJECT_ROOT / "data" / "raw" / "fixed_income" / "etf"
SNAPSHOT_DIR = RAW_DIR / "tsetmc_snapshots"
CSV_PATH = RAW_DIR / "etemad.csv"
INSTRUMENT_CODE = "66818022341772870"
INSTRUMENT_NAME = "صندوق س.اعتماد آفرین پارسیان-د"
TICKER = "اعتماد"
API_URL = (
    "https://cdn.tsetmc.com/api/ClosingPrice/"
    f"GetClosingPriceDailyList/{INSTRUMENT_CODE}/0"
)
CSV_FIELDS = (
    "source_date_gregorian", "ins_code", "ticker", "instrument_name",
    "closing_price_irr", "last_trade_price_irr", "previous_closing_price_irr",
    "first_price_irr", "low_price_irr", "high_price_irr", "trade_count",
    "trade_volume", "trade_value_irr", "has_trade",
)


def request_payload(timeout_seconds: int = 60) -> bytes:
    response = requests.get(API_URL, headers={"User-Agent": "asset-allocation-research/0.1"}, timeout=timeout_seconds)
    response.raise_for_status()
    return response.content


def parse_records(payload: bytes) -> list[dict[str, Any]]:
    raw_records = json.loads(payload.decode("utf-8")).get("closingPriceDaily")
    if not isinstance(raw_records, list) or not raw_records:
        raise ValueError("TSETMC payload has no non-empty closingPriceDaily list")
    records: dict[str, dict[str, Any]] = {}
    for source in raw_records:
        raw_date = str(source.get("dEven", ""))
        if len(raw_date) != 8 or not raw_date.isdecimal():
            raise ValueError(f"Invalid TSETMC Gregorian date: {raw_date!r}")
        date = datetime.strptime(raw_date, "%Y%m%d").date().isoformat()
        closing = _number(source, "pClosing")
        if closing <= 0:
            raise ValueError(f"Non-positive closing price on {date}: {closing}")
        volume, trades = _number(source, "qTotTran5J"), _number(source, "zTotTran")
        record = {
            "source_date_gregorian": date, "ins_code": INSTRUMENT_CODE, "ticker": TICKER,
            "instrument_name": INSTRUMENT_NAME, "closing_price_irr": _format(closing),
            "last_trade_price_irr": _format(_number(source, "pDrCotVal")),
            "previous_closing_price_irr": _format(_number(source, "priceYesterday")),
            "first_price_irr": _format(_number(source, "priceFirst")),
            "low_price_irr": _format(_number(source, "priceMin")),
            "high_price_irr": _format(_number(source, "priceMax")),
            "trade_count": _format(trades), "trade_volume": _format(volume),
            "trade_value_irr": _format(_number(source, "qTotCap")),
            "has_trade": str(trades > 0 and volume > 0).lower(),
        }
        if date in records and records[date] != record:
            raise ValueError(f"Conflicting duplicate date in API response: {date}")
        records[date] = record
    return [records[date] for date in sorted(records)]


def collect() -> dict[str, str | int]:
    payload = request_payload()
    snapshot = archive_snapshot(payload)
    records = parse_records(payload)
    write_canonical_csv(records)
    traded = [row for row in records if row["has_trade"] == "true"]
    return {
        "records": len(records), "first_api_date": records[0]["source_date_gregorian"],
        "first_positive_trade_date": traded[0]["source_date_gregorian"] if traded else "",
        "last_api_date": records[-1]["source_date_gregorian"], "snapshot": str(snapshot),
        "csv": str(CSV_PATH), "retrieved_at_utc": datetime.now(UTC).isoformat(),
    }


def archive_snapshot(payload: bytes) -> Path:
    SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)
    path = SNAPSHOT_DIR / f"{hashlib.sha256(payload).hexdigest()}.json"
    if not path.exists():
        _atomic_write_bytes(path, payload)
    return path


def write_canonical_csv(records: list[dict[str, Any]]) -> None:
    if not records:
        raise ValueError("Refusing to write an empty canonical CSV")
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", delete=False, dir=RAW_DIR, suffix=".tmp") as file:
        writer = csv.DictWriter(file, fieldnames=CSV_FIELDS)
        writer.writeheader()
        writer.writerows(records)
        temporary = Path(file.name)
    os.replace(temporary, CSV_PATH)


def _number(record: dict[str, Any], field: str) -> float:
    value = record.get(field, 0)
    if value is None:
        return 0.0
    if not isinstance(value, int | float):
        raise ValueError(f"Non-numeric {field}: {value!r}")
    return float(value)


def _format(value: float) -> str:
    return str(int(value)) if value.is_integer() else str(value)


def _atomic_write_bytes(path: Path, payload: bytes) -> None:
    with tempfile.NamedTemporaryFile("wb", delete=False, dir=path.parent, suffix=".tmp") as file:
        file.write(payload)
        temporary = Path(file.name)
    os.replace(temporary, path)


if __name__ == "__main__":
    print(json.dumps(collect(), ensure_ascii=False, indent=2))
