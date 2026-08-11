"""Reusable incremental collector for continuous IME commodity certificates."""

from __future__ import annotations

import argparse
import csv
import json
import shutil
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any


API_URL = "https://dataapi.ime.co.ir/api/CDC/CDCTrades"
MARKET_ID = 22
FIRST_QUERY_DATE = date(2025, 10, 20)
MAX_CHUNK_DAYS = 180
PAGE_SIZE = 100
RAW_COLUMNS = [
    "ROW", "CommodityID", "ContractCode", "ContractDescription",
    "TradesVolume", "TradesValue", "MaxPrice", "MinPrice", "LastPrice",
    "FirstPrice", "OpenInterest", "ChangeOpenInterest", "ActiveCustomers",
    "ActiveBrokers", "C_Buy", "C_Sell", "Vol_Hoghooghi_Buy",
    "Val_Hoghooghi_Buy", "Vol_Hoghooghi_Sell", "Val_Hoghooghi_Sell",
    "Vol_Haghighi_Buy", "Val_Haghighi_Buy", "Vol_Haghighi_Sell",
    "Val_Haghighi_Sell", "LastSettlementPrice", "TodaySettlementPrice",
    "SettlementPricePercent", "DT", "PersianDate", "DeliveryDate",
    "fetched_at_utc", "source_url",
]


@dataclass(frozen=True)
class CertificateConfig:
    slug: str
    title_fa: str
    commodity_id: str
    contract_description: str
    old_code: str
    new_code: str
    csv_name: str

    @property
    def codes(self) -> frozenset[str]:
        return frozenset((self.old_code, self.new_code))


def chunks(start: date, end: date):
    cursor = start
    while cursor <= end:
        chunk_end = min(cursor + timedelta(days=MAX_CHUNK_DAYS - 1), end)
        yield cursor, chunk_end
        cursor = chunk_end + timedelta(days=1)


def curl_json(payload: dict[str, Any], timeout: int, retries: int) -> dict[str, Any]:
    curl = shutil.which("curl.exe") or shutil.which("curl")
    if curl is None:
        raise RuntimeError("curl was not found; install curl or add it to PATH")
    command = [
        curl, "-4", "--tlsv1.2", "--silent", "--show-error",
        "--connect-timeout", str(min(timeout, 30)), "--max-time", str(timeout),
        "--header", "User-Agent: Mozilla/5.0",
        "--header", "Origin: https://gold.ime.co.ir",
        "--header", "Referer: https://gold.ime.co.ir/",
        "--header", "Content-Type: application/json; charset=utf-8",
        "--data-binary", "@-", API_URL,
    ]
    encoded = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    last_error = ""
    for attempt in range(1, retries + 1):
        result = subprocess.run(
            command, input=encoded, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, check=False,
        )
        if result.returncode == 0:
            try:
                response = json.loads(result.stdout.decode("utf-8-sig"))
            except json.JSONDecodeError:
                last_error = f"non-JSON response: {result.stdout[:200]!r}"
            else:
                if not isinstance(response, dict):
                    raise ValueError("Unexpected non-object response from IME")
                if response.get("Success") is False:
                    raise RuntimeError(f"IME reported failure: {response.get('Messages')}")
                return response
        else:
            last_error = result.stderr.decode("utf-8", errors="replace").strip()
        if attempt < retries:
            time.sleep(2 ** (attempt - 1))
    raise RuntimeError(f"IME request failed after {retries} attempts: {last_error}")


def fetch(start: date, end: date, config: CertificateConfig, timeout: int, retries: int):
    page_number = 1
    raw_pages: list[dict[str, Any]] = []
    selected: list[dict[str, Any]] = []
    while True:
        payload = {
            "fromDate": start.isoformat(), "toDate": end.isoformat(),
            "pageNumber": page_number, "pageSize": PAGE_SIZE,
            "marketId": MARKET_ID, "customFilter": "",
        }
        response = curl_json(payload, timeout, retries)
        rows = response.get("Data", [])
        if not isinstance(rows, list):
            raise ValueError("IME response Data field is not a list")
        raw_pages.append(response)
        selected.extend(row for row in rows if str(row.get("ContractCode")) in config.codes)
        if not response.get("HasNextPage", False):
            break
        page_number += 1
        if page_number > 100:
            raise RuntimeError("IME pagination exceeded the safety limit")
    return raw_pages, selected


def read_existing(path: Path) -> dict[str, dict[str, str]]:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames != RAW_COLUMNS:
            raise ValueError(f"Unexpected columns in {path}: {reader.fieldnames}")
        rows = list(reader)
    if len(rows) != len({row["DT"][:10] for row in rows}):
        raise ValueError(f"Duplicate dates in existing dataset: {path}")
    return {row["DT"][:10]: row for row in rows}


def validate_record(record: dict[str, Any], config: CertificateConfig) -> None:
    missing = [column for column in RAW_COLUMNS[:-2] if column not in record]
    if missing:
        raise ValueError(f"IME schema changed; missing fields: {missing}")
    if str(record["ContractCode"]) not in config.codes:
        raise ValueError(f"Unexpected contract code: {record['ContractCode']}")
    if str(record["CommodityID"]) != config.commodity_id:
        raise ValueError(f"Unexpected CommodityID: {record['CommodityID']}")
    if str(record["ContractDescription"]).strip() != config.contract_description:
        raise ValueError(f"Unexpected description: {record['ContractDescription']!r}")
    datetime.fromisoformat(str(record["DT"]).replace("Z", "+00:00"))
    numeric_nonnegative = (
        "TradesVolume", "TradesValue", "MaxPrice", "MinPrice", "LastPrice",
        "FirstPrice", "OpenInterest", "TodaySettlementPrice",
    )
    for field in numeric_nonnegative:
        if float(record[field] or 0) < 0:
            raise ValueError(f"Negative {field} on {record['DT']}")
    volume = float(record["TradesVolume"] or 0)
    value = float(record["TradesValue"] or 0)
    settlement = float(record["TodaySettlementPrice"] or 0)
    if volume > 0:
        if value <= 0 or settlement <= 0:
            raise ValueError(f"Positive volume with non-positive value/price on {record['DT']}")
        vwap = value / volume
        if abs(vwap - settlement) > max(0.51, settlement * 1e-7):
            raise ValueError(
                f"VWAP/settlement mismatch on {record['DT']}: {vwap} vs {settlement}"
            )


def normalize(record: dict[str, Any], config: CertificateConfig, fetched_at: str):
    validate_record(record, config)
    output = {column: record.get(column) for column in RAW_COLUMNS[:-2]}
    output.update(fetched_at_utc=fetched_at, source_url=API_URL)
    return output


def write_atomic(path: Path, records: dict[str, dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=RAW_COLUMNS)
        writer.writeheader()
        for key in sorted(records):
            writer.writerow(records[key])
    temporary.replace(path)


def collect(project_dir: Path, config: CertificateConfig, timeout: int, retries: int,
            refresh_days: int, full_refresh: bool = False) -> Path:
    raw_dir = project_dir / "data" / "raw" / "certificate"
    csv_path = raw_dir / config.csv_name
    snapshots = raw_dir / "api_snapshots"
    existing = read_existing(csv_path)
    today = date.today()
    if existing and not full_refresh:
        start = max(FIRST_QUERY_DATE, date.fromisoformat(max(existing)) - timedelta(days=refresh_days))
    else:
        start = FIRST_QUERY_DATE
    if start > today:
        raise ValueError(f"Start date {start} is later than today {today}")

    fetched_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    fetched: dict[str, dict[str, Any]] = {}
    snapshots.mkdir(parents=True, exist_ok=True)
    print(f"Commodity: {config.title_fa}")
    print(f"Existing rows: {len(existing)}")
    print(f"Query period: {start} through {today}")
    for chunk_start, chunk_end in chunks(start, today):
        pages, rows = fetch(chunk_start, chunk_end, config, timeout, retries)
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        snapshot_path = snapshots / f"cdc_{chunk_start}_{chunk_end}_{stamp}.json"
        snapshot = {
            "request": {
                "fromDate": chunk_start.isoformat(), "toDate": chunk_end.isoformat(),
                "marketId": MARKET_ID, "contractCodesAppliedLocally": sorted(config.codes),
            },
            "commodity": config.__dict__, "fetched_at_utc": fetched_at,
            "source_url": API_URL, "pages": pages,
        }
        snapshot_path.write_text(
            json.dumps(snapshot, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        for record in rows:
            normalized = normalize(record, config, fetched_at)
            key = str(normalized["DT"])[:10]
            if key in fetched:
                raise ValueError(f"Multiple selected records for {key}")
            fetched[key] = normalized
        print(f"  {chunk_start}..{chunk_end}: {len(pages)} pages, {len(rows)} selected rows")

    merged = fetched if full_refresh else existing | fetched
    if not merged:
        raise ValueError(f"No records found for {config.title_fa}")
    write_atomic(csv_path, merged)
    traded = sum(float(row["TradesVolume"] or 0) > 0 for row in merged.values())
    codes = sorted({str(row["ContractCode"]) for row in merged.values()})
    print(f"Saved rows: {len(merged)} ({traded} with trades)")
    print(f"Coverage: {min(merged)} through {max(merged)}")
    print(f"Contract codes: {', '.join(codes)}")
    print(f"Output: {csv_path}")
    return csv_path


def run_cli(project_dir: Path, config: CertificateConfig) -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(
        description=f"Incrementally collect {config.title_fa} certificate data"
    )
    parser.add_argument("--timeout", type=int, default=60)
    parser.add_argument("--retries", type=int, default=3)
    parser.add_argument("--refresh-days", type=int, default=14)
    parser.add_argument("--full-refresh", action="store_true")
    args = parser.parse_args()
    collect(project_dir, config, args.timeout, args.retries, args.refresh_days, args.full_refresh)
