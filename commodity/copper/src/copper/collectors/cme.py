"""Collect official CME COMEX copper warehouse-stock workbooks via preserved captures."""

from __future__ import annotations

import argparse
import csv
import io
import json
import re
import time
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import requests
import truststore


PROJECT_DIR = Path(__file__).resolve().parents[3]
SOURCE_DIR = PROJECT_DIR / "data" / "raw" / "global_market" / "cme"
ORIGINAL_URL = "https://www.cmegroup.com/delivery_reports/Copper_Stocks.xls"
CDX_URL = "https://web.archive.org/cdx/search/cdx"
FIELDS = [
    "report_date", "activity_date", "delivery_point", "stock_status", "previous_total_short_tons",
    "received_short_tons", "withdrawn_short_tons", "net_change_short_tons", "adjustment_short_tons",
    "total_today_short_tons", "archive_capture_utc", "original_source_url", "replay_url",
]


def iso_date(value: str) -> str:
    return pd.to_datetime(value, errors="raise").date().isoformat()


def find_dates(table: pd.DataFrame) -> tuple[str, str]:
    report_date = activity_date = ""
    for raw_value in table.to_numpy().ravel():
        value = str(raw_value)
        report = re.search(r"Report Date:\s*(\d{1,2}/\d{1,2}/\d{4})", value)
        activity = re.search(r"Activity Date:\s*(\d{1,2}/\d{1,2}/\d{4})", value)
        if report:
            report_date = iso_date(report.group(1))
        if activity:
            activity_date = iso_date(activity.group(1))
    if not report_date or not activity_date:
        raise RuntimeError("CME workbook is missing report/activity dates")
    return report_date, activity_date


def numeric(value: object) -> float | None:
    if pd.isna(value) or str(value).strip() in {"", "-", "--"}:
        return None
    return float(str(value).replace(",", ""))


def parse_workbook(payload: bytes, capture: str, replay_url: str) -> list[dict]:
    table = pd.read_excel(io.BytesIO(payload), sheet_name=0, header=None, engine="xlrd")
    report_date, activity_date = find_dates(table)
    header_rows = table.index[table.iloc[:, 0].astype(str).str.strip().eq("DELIVERY POINT")].tolist()
    if len(header_rows) != 1:
        raise RuntimeError(f"Expected one CME stock header, found {len(header_rows)}")
    header = header_rows[0]
    rows: list[dict] = []
    delivery_point = ""
    for index in range(header + 1, len(table)):
        label = str(table.iloc[index, 0]).strip()
        lowered = label.lower()
        status = ""
        point = delivery_point
        if lowered.startswith("total registered"):
            point, status = "EXCHANGE_TOTAL", "registered"
        elif lowered.startswith("total eligible"):
            point, status = "EXCHANGE_TOTAL", "eligible"
        elif lowered == "total copper":
            point, status = "EXCHANGE_TOTAL", "total"
        elif lowered.startswith("registered"):
            status = "registered"
        elif lowered.startswith("eligible"):
            status = "eligible"
        elif lowered == "total" and delivery_point:
            status = "total"
        elif label and label == label.upper() and not any(char.isdigit() for char in label):
            delivery_point = label
            continue
        if not status or not point:
            continue
        values = [numeric(table.iloc[index, column]) for column in range(2, 8)]
        if all(value is None for value in values):
            continue
        rows.append(dict(zip(FIELDS, [
            report_date, activity_date, point, status, *values, capture, ORIGINAL_URL, replay_url,
        ])))
    if not any(row["delivery_point"] == "EXCHANGE_TOTAL" for row in rows):
        raise RuntimeError(f"CME workbook {capture} lacks exchange totals")
    return rows


def capture_index(session: requests.Session, timeout: int) -> list[dict]:
    params = {
        "url": "www.cmegroup.com/delivery_reports/Copper_Stocks.xls",
        "output": "json",
        "filter": "statuscode:200",
        "fl": "timestamp,original,statuscode,mimetype,digest,length",
        "collapse": "digest",
    }
    response = session.get(CDX_URL, params=params, timeout=timeout)
    response.raise_for_status()
    document = response.json()
    header = document[0]
    return [dict(zip(header, row)) for row in document[1:]]


def get_with_retries(session: requests.Session, url: str, timeout: int, retries: int = 5) -> bytes:
    last_error: Exception | None = None
    for attempt in range(retries):
        try:
            response = session.get(url, timeout=timeout)
            response.raise_for_status()
            if response.content[:8] != b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1":
                raise RuntimeError("Response is not a legacy XLS workbook")
            return response.content
        except (requests.RequestException, RuntimeError) as error:
            last_error = error
            if attempt + 1 < retries:
                time.sleep(2 ** attempt)
    raise RuntimeError(f"Failed to download {url}") from last_error


def collect(timeout: int, delay: float) -> tuple[Path, int]:
    truststore.inject_into_ssl()
    session = requests.Session()
    session.headers["User-Agent"] = "Mozilla/5.0 empirical-economics-research"
    SOURCE_DIR.mkdir(parents=True, exist_ok=True)
    snapshots = SOURCE_DIR / "snapshots"
    snapshots.mkdir(exist_ok=True)
    captures = capture_index(session, timeout)
    manifest_rows: list[dict] = []
    parsed: list[dict] = []
    for index, capture in enumerate(captures, start=1):
        timestamp = capture["timestamp"]
        replay_url = f"https://web.archive.org/web/{timestamp}id_/{capture['original']}"
        snapshot = snapshots / f"cme_copper_stocks_{timestamp}.xls"
        if snapshot.exists():
            payload = snapshot.read_bytes()
        else:
            payload = get_with_retries(session, replay_url, timeout)
            with snapshot.open("xb") as handle:
                handle.write(payload)
            time.sleep(delay)
        error = ""
        try:
            rows = parse_workbook(payload, timestamp, replay_url)
            parsed.extend(rows)
        except Exception as exc:
            error = f"{type(exc).__name__}: {exc}"
        manifest_rows.append(capture | {"replay_url": replay_url, "snapshot": snapshot.name, "parse_error": error})
        if index % 20 == 0:
            print(f"cme stocks: processed {index}/{len(captures)} captures", flush=True)
    manifest = SOURCE_DIR / "cme_copper_stocks_capture_manifest.csv"
    manifest_fields = list(manifest_rows[0])
    temporary_manifest = manifest.with_suffix(".csv.tmp")
    with temporary_manifest.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=manifest_fields)
        writer.writeheader()
        writer.writerows(manifest_rows)
    temporary_manifest.replace(manifest)
    errors = [row for row in manifest_rows if row["parse_error"]]
    if errors:
        raise RuntimeError(f"{len(errors)} CME captures failed parsing; see {manifest}")
    latest_by_activity: dict[str, str] = {}
    for row in parsed:
        latest_by_activity[row["activity_date"]] = max(
            latest_by_activity.get(row["activity_date"], ""), row["archive_capture_utc"]
        )
    rows = [row for row in parsed if row["archive_capture_utc"] == latest_by_activity[row["activity_date"]]]
    rows.sort(key=lambda row: (row["activity_date"], row["delivery_point"], row["stock_status"]))
    keys = [(row["activity_date"], row["delivery_point"], row["stock_status"]) for row in rows]
    if len(keys) != len(set(keys)):
        raise RuntimeError("Duplicate CME activity-date/delivery-point/status keys")
    output = SOURCE_DIR / "comex_copper_stocks_raw.csv"
    temporary = output.with_suffix(".csv.tmp")
    with temporary.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    temporary.replace(output)
    print(f"cme stocks: {len(captures)} distinct official workbooks; {len(rows)} canonical rows")
    return output, len(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--timeout", type=int, default=120)
    parser.add_argument("--delay", type=float, default=0.2)
    args = parser.parse_args()
    path, count = collect(args.timeout, args.delay)
    print(f"cme stocks: {count:,} rows -> {path}")


if __name__ == "__main__":
    main()
