"""Collect official SHFE copper futures Daily Express JSON files."""

from __future__ import annotations

import argparse
import csv
import json
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import date, timedelta
from pathlib import Path

import requests
import truststore


PROJECT_DIR = Path(__file__).resolve().parents[3]
SOURCE_DIR = PROJECT_DIR / "data" / "raw" / "global_market" / "shfe"
URL = "https://www.shfe.com.cn/data/tradedata/future/dailydata/kx{date}.dat"
FIELDS = [
    "trade_date", "contract", "delivery_month", "previous_settlement_cny_per_tonne",
    "open_cny_per_tonne", "high_cny_per_tonne", "low_cny_per_tonne",
    "close_cny_per_tonne", "settlement_cny_per_tonne", "close_change_cny_per_tonne",
    "settlement_change_cny_per_tonne", "volume_lots", "open_interest_lots",
    "open_interest_change_lots", "turnover_10000_cny", "source_url", "snapshot",
]


def weekdays(start: date, end: date) -> list[date]:
    values = []
    current = start
    while current <= end:
        if current.weekday() < 5:
            values.append(current)
        current += timedelta(days=1)
    return values


def value(row: dict, key: str) -> object | None:
    result = row.get(key)
    return None if result in {"", None} else result


def parse_payload(payload: bytes, source_url: str, snapshot: str) -> list[dict]:
    document = json.loads(payload)
    trade_date = str(document.get("report_date") or snapshot.rsplit("_", 1)[-1].removesuffix(".json"))
    rows = []
    for source in document.get("o_curinstrument", []):
        if str(source.get("PRODUCTID", "")).strip() != "cu_f" or not str(source.get("DELIVERYMONTH", "")).strip().isdigit():
            continue
        month = str(source["DELIVERYMONTH"]).strip()
        year = 2000 + int(month[:2])
        rows.append(dict(zip(FIELDS, [
            f"{trade_date[:4]}-{trade_date[4:6]}-{trade_date[6:]}", f"cu{month}",
            f"{year:04d}-{month[2:]}", value(source, "PRESETTLEMENTPRICE"),
            value(source, "OPENPRICE"), value(source, "HIGHESTPRICE"),
            value(source, "LOWESTPRICE"), value(source, "CLOSEPRICE"),
            value(source, "SETTLEMENTPRICE"), value(source, "ZD1_CHG"),
            value(source, "ZD2_CHG"), value(source, "VOLUME"),
            value(source, "OPENINTEREST"), value(source, "OPENINTERESTCHG"),
            value(source, "TURNOVER"), source_url, snapshot,
        ])))
    return rows


def fetch(day: date, timeout: int) -> tuple[date, str, bytes | None, str]:
    url = URL.format(date=day.strftime("%Y%m%d"))
    for attempt in range(4):
        try:
            response = requests.get(url, headers={"User-Agent": "Mozilla/5.0 empirical-research"}, timeout=timeout)
            if response.status_code == 404:
                return day, url, None, "not_published"
            response.raise_for_status()
            if not response.content.lstrip().startswith(b"{"):
                raise RuntimeError("response is not JSON")
            return day, url, response.content, "downloaded"
        except (requests.RequestException, RuntimeError) as error:
            if attempt == 3:
                return day, url, None, f"error:{type(error).__name__}:{error}"
            time.sleep(2 ** attempt)
    raise AssertionError("unreachable")


def collect(start: date, end: date, timeout: int, workers: int) -> tuple[Path, int]:
    truststore.inject_into_ssl()
    SOURCE_DIR.mkdir(parents=True, exist_ok=True)
    snapshots = SOURCE_DIR / "daily_express_snapshots"
    snapshots.mkdir(exist_ok=True)
    pending = []
    manifest_rows = []
    for day in weekdays(start, end):
        snapshot = snapshots / f"shfe_daily_express_{day:%Y%m%d}.json"
        if snapshot.exists():
            manifest_rows.append({"date": day.isoformat(), "url": URL.format(date=f"{day:%Y%m%d}"), "snapshot": snapshot.name, "status": "preserved"})
        else:
            pending.append(day)
    with ThreadPoolExecutor(max_workers=workers) as executor:
        for index, (day, url, payload, status) in enumerate(executor.map(lambda d: fetch(d, timeout), pending), start=1):
            snapshot = snapshots / f"shfe_daily_express_{day:%Y%m%d}.json"
            if payload is not None:
                with snapshot.open("xb") as handle:
                    handle.write(payload)
            manifest_rows.append({"date": day.isoformat(), "url": url, "snapshot": snapshot.name if payload else "", "status": status})
            if index % 250 == 0:
                print(f"shfe daily: checked {index}/{len(pending)} new weekdays", flush=True)
    errors = [row for row in manifest_rows if row["status"].startswith("error:")]
    manifest_rows.sort(key=lambda row: row["date"])
    manifest = SOURCE_DIR / "shfe_daily_express_manifest.csv"
    temporary_manifest = manifest.with_suffix(".csv.tmp")
    with temporary_manifest.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(manifest_rows[0]))
        writer.writeheader()
        writer.writerows(manifest_rows)
    temporary_manifest.replace(manifest)
    if errors:
        raise RuntimeError(f"{len(errors)} SHFE requests failed; see {manifest}")
    rows = []
    for snapshot in sorted(snapshots.glob("shfe_daily_express_*.json")):
        url = URL.format(date=snapshot.stem.rsplit("_", 1)[-1])
        rows.extend(parse_payload(snapshot.read_bytes(), url, snapshot.name))
    rows.sort(key=lambda row: (row["trade_date"], row["contract"]))
    keys = [(row["trade_date"], row["contract"]) for row in rows]
    if len(keys) != len(set(keys)):
        raise RuntimeError("duplicate SHFE trade-date/contract keys")
    output = SOURCE_DIR / "shfe_copper_futures_daily_raw.csv"
    temporary = output.with_suffix(".csv.tmp")
    with temporary.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    temporary.replace(output)
    print(f"shfe daily: {len(rows):,} copper contract rows from {len(set(d for d, _ in keys)):,} dates")
    return output, len(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--start", type=date.fromisoformat, default=date(2008, 1, 1))
    parser.add_argument("--end", type=date.fromisoformat, default=date.today())
    parser.add_argument("--timeout", type=int, default=45)
    parser.add_argument("--workers", type=int, default=12)
    args = parser.parse_args()
    path, count = collect(args.start, args.end, args.timeout, args.workers)
    print(f"shfe daily: {count:,} rows -> {path}")


if __name__ == "__main__":
    main()
