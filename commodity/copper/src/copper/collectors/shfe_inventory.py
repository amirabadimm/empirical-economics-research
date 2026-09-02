"""Collect official SHFE copper daily warrants and weekly inventory reports."""

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
DAILY_URL = "https://www.shfe.com.cn/data/tradedata/future/dailydata/{date}dailystock.dat"
WEEKLY_URL = "https://www.shfe.com.cn/data/tradedata/future/weeklydata/{date}weeklystock.dat"


def english(value: object) -> str:
    text = str(value or "").strip()
    return text.split("$$", 1)[-1].strip()


def parse_totals(payload: bytes, source_url: str, snapshot: str, frequency: str) -> list[dict]:
    document = json.loads(payload)
    raw_date = str(document.get("report_date") or document.get("o_tradingday") or snapshot.split("_")[-1].split(".")[0])
    report_date = f"{raw_date[:4]}-{raw_date[4:6]}-{raw_date[6:8]}"
    rows = []
    for source in document.get("o_cursor", []):
        is_copper = str(source.get("VARID", "")).strip() == "cu" or english(source.get("VARNAME")).upper() == "COPPER"
        if not is_copper or str(source.get("ROWSTATUS")) != "2":
            continue
        rows.append({
            "report_date": report_date,
            "inventory_category": english(source.get("WHABBRNAME")),
            "inventory_tonnes": source.get("SPOTWGHTS") if frequency == "weekly" else None,
            "inventory_change_tonnes": source.get("SPOTCHANGE") if frequency == "weekly" else None,
            "warrants_tonnes": source.get("WRTWGHTS"),
            "warrant_change_tonnes": source.get("WRTCHANGE"),
            "warehouse_capacity_tonnes": source.get("WHSTOCKS") if frequency == "weekly" else None,
            "frequency": frequency,
            "source_url": source_url,
            "snapshot": snapshot,
        })
    return rows


def dates(start: date, end: date, weekly: bool) -> list[date]:
    values = []
    current = start
    while current <= end:
        if current.weekday() == 4 if weekly else current.weekday() < 5:
            values.append(current)
        current += timedelta(days=1)
    return values


def fetch(task: tuple[date, str, str], timeout: int) -> tuple[date, str, str, bytes | None]:
    day, frequency, template = task
    url = template.format(date=f"{day:%Y%m%d}")
    last_error: Exception | None = None
    for attempt in range(5):
        try:
            response = requests.get(url, headers={"User-Agent": "Mozilla/5.0 empirical-research"}, timeout=timeout)
            if response.status_code == 404:
                return day, frequency, url, None
            response.raise_for_status()
            if not response.content.lstrip().startswith(b"{"):
                raise RuntimeError(f"non-JSON SHFE response: {url}")
            return day, frequency, url, response.content
        except (requests.RequestException, RuntimeError) as error:
            last_error = error
            if attempt < 4:
                time.sleep(2 ** attempt)
    raise RuntimeError(f"failed SHFE report after retries: {url}") from last_error


def collect(start: date, end: date, timeout: int, workers: int) -> tuple[Path, Path]:
    truststore.inject_into_ssl()
    SOURCE_DIR.mkdir(parents=True, exist_ok=True)
    tasks = [(day, "daily", DAILY_URL) for day in dates(start, end, False)]
    tasks += [(day, "weekly", WEEKLY_URL) for day in dates(start, end, True)]
    pending = []
    for task in tasks:
        day, frequency, _ = task
        snapshot = SOURCE_DIR / f"{frequency}_inventory_snapshots" / f"shfe_{frequency}_inventory_{day:%Y%m%d}.json"
        if not snapshot.exists():
            pending.append(task)
    with ThreadPoolExecutor(max_workers=workers) as executor:
        for index, (day, frequency, _, payload) in enumerate(executor.map(lambda task: fetch(task, timeout), pending), 1):
            if payload is not None:
                folder = SOURCE_DIR / f"{frequency}_inventory_snapshots"
                folder.mkdir(exist_ok=True)
                with (folder / f"shfe_{frequency}_inventory_{day:%Y%m%d}.json").open("xb") as handle:
                    handle.write(payload)
            if index % 250 == 0:
                print(f"shfe inventory: checked {index}/{len(pending)} reports", flush=True)
    outputs = []
    fields = ["report_date", "inventory_category", "inventory_tonnes", "inventory_change_tonnes", "warrants_tonnes", "warrant_change_tonnes", "warehouse_capacity_tonnes", "frequency", "source_url", "snapshot"]
    for frequency, template in [("daily", DAILY_URL), ("weekly", WEEKLY_URL)]:
        rows = []
        folder = SOURCE_DIR / f"{frequency}_inventory_snapshots"
        for snapshot in sorted(folder.glob("*.json")) if folder.exists() else []:
            stamp = snapshot.stem.rsplit("_", 1)[-1]
            rows.extend(parse_totals(snapshot.read_bytes(), template.format(date=stamp), snapshot.name, frequency))
        rows.sort(key=lambda row: (row["report_date"], row["inventory_category"]))
        output = SOURCE_DIR / f"shfe_copper_{'warrants_daily' if frequency == 'daily' else 'inventory_weekly'}_raw.csv"
        temporary = output.with_suffix(".csv.tmp")
        with temporary.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fields)
            writer.writeheader()
            writer.writerows(rows)
        temporary.replace(output)
        print(f"shfe {frequency}: {len(rows):,} copper total-category rows")
        outputs.append(output)
    return outputs[0], outputs[1]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--start", type=date.fromisoformat, default=date(2014, 1, 1))
    parser.add_argument("--end", type=date.fromisoformat, default=date.today())
    parser.add_argument("--timeout", type=int, default=45)
    parser.add_argument("--workers", type=int, default=12)
    args = parser.parse_args()
    collect(args.start, args.end, args.timeout, args.workers)


if __name__ == "__main__":
    main()
