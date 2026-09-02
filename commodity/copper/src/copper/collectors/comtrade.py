"""Collect China monthly copper trade from the official UN Comtrade preview API."""

from __future__ import annotations

import argparse
import csv
import json
import time
from datetime import datetime, timezone
from pathlib import Path

import requests
import truststore


PROJECT_DIR = Path(__file__).resolve().parents[3]
SOURCE_DIR = PROJECT_DIR / "data" / "raw" / "global_market" / "comtrade"
API_URL = "https://comtradeapi.un.org/public/v1/preview/C/M/HS"
FIELDS = [
    "period", "refYear", "refMonth", "reporterCode", "flowCode", "partnerCode",
    "classificationCode", "isOriginalClassification", "cmdCode", "customsCode",
    "motCode", "qtyUnitCode", "qty", "isQtyEstimated", "netWgt",
    "isNetWgtEstimated", "grossWgt", "isGrossWgtEstimated", "cifvalue",
    "fobvalue", "primaryValue", "isReported", "isAggregate", "source_url",
    "source_access_tier", "fetched_at_utc",
]


def month_range(start: str, end: str) -> list[str]:
    start_year, start_month = int(start[:4]), int(start[4:])
    end_year, end_month = int(end[:4]), int(end[4:])
    result: list[str] = []
    year, month = start_year, start_month
    while (year, month) <= (end_year, end_month):
        result.append(f"{year:04d}{month:02d}")
        year, month = (year + 1, 1) if month == 12 else (year, month + 1)
    return result


def previous_month() -> str:
    now = datetime.now(timezone.utc)
    year, month = (now.year - 1, 12) if now.month == 1 else (now.year, now.month - 1)
    return f"{year:04d}{month:02d}"


def fetch_month(session: requests.Session, period: str, timeout: int, retries: int) -> bytes:
    params = {
        "reporterCode": "156",
        "period": period,
        "partnerCode": "0",
        "cmdCode": "2603,7403,7404",
        "flowCode": "M,X",
    }
    last_error: Exception | None = None
    for attempt in range(retries):
        try:
            response = session.get(API_URL, params=params, timeout=timeout)
            if response.status_code == 429:
                time.sleep(max(float(response.headers.get("Retry-After", 10)), 10))
                continue
            response.raise_for_status()
            document = response.json()
            if document.get("error"):
                raise RuntimeError(f"Comtrade error for {period}: {document['error']}")
            return response.content
        except (requests.RequestException, ValueError, RuntimeError) as error:
            last_error = error
            if attempt + 1 < retries:
                time.sleep(min(2 ** attempt, 30))
    raise RuntimeError(f"Comtrade failed for {period}") from last_error


def collect(start: str, end: str, refresh_months: int, timeout: int, delay: float) -> tuple[Path, int]:
    truststore.inject_into_ssl()
    session = requests.Session()
    session.headers["User-Agent"] = "empirical-economics-research copper collector/1.0"
    snapshots = SOURCE_DIR / "snapshots"
    snapshots.mkdir(parents=True, exist_ok=True)
    periods = month_range(start, end)
    refresh = set(periods[-refresh_months:]) if refresh_months else set()
    rows: list[dict] = []
    for index, period in enumerate(periods, start=1):
        period_dir = snapshots / period
        period_dir.mkdir(exist_ok=True)
        existing = sorted(period_dir.glob("*.json"))
        if existing and period not in refresh:
            payload = existing[-1].read_bytes()
        else:
            payload = fetch_month(session, period, timeout, retries=6)
            stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
            with (period_dir / f"china_copper_trade_{period}_{stamp}.json").open("xb") as handle:
                handle.write(payload)
            time.sleep(delay)
        document = json.loads(payload)
        fetched_at = datetime.now(timezone.utc).isoformat()
        for item in document.get("data", []):
            if str(item.get("cmdCode")) not in {"2603", "7403", "7404"}:
                continue
            row = {field: item.get(field) for field in FIELDS}
            row["source_url"] = API_URL
            row["source_access_tier"] = "unauthenticated_preview_incomplete"
            row["fetched_at_utc"] = fetched_at
            rows.append(row)
        if index % 24 == 0:
            print(f"comtrade: processed {index}/{len(periods)} months", flush=True)
    rows.sort(key=lambda row: (row["period"], row["cmdCode"], row["flowCode"]))
    keys = [(row["period"], row["cmdCode"], row["flowCode"]) for row in rows]
    if len(keys) != len(set(keys)):
        raise RuntimeError("Duplicate Comtrade period/commodity/flow keys")
    SOURCE_DIR.mkdir(parents=True, exist_ok=True)
    output = SOURCE_DIR / "china_copper_trade_raw.csv"
    temporary = output.with_suffix(".csv.tmp")
    with temporary.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    temporary.replace(output)
    return output, len(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--start", default="200001")
    parser.add_argument("--end", default=previous_month())
    parser.add_argument("--refresh-months", type=int, default=3)
    parser.add_argument("--timeout", type=int, default=60)
    parser.add_argument("--delay", type=float, default=1.5)
    args = parser.parse_args()
    path, count = collect(args.start, args.end, args.refresh_months, args.timeout, args.delay)
    print(f"comtrade: {count:,} rows -> {path}")


if __name__ == "__main__":
    main()
