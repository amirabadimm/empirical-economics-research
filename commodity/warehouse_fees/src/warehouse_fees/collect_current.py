"""Snapshot and parse the official IME current warehouse-fee table."""

from __future__ import annotations

import csv
import hashlib
from datetime import datetime, timezone
from pathlib import Path

import requests
from bs4 import BeautifulSoup

SOURCE_URL = "https://www.ime.co.ir/WarehousesFee.html"
COLUMNS = [
    "asset_fa", "daily_storage_fee_text_fa", "assessment_fee_text_fa",
    "source_url", "fetched_at_utc", "snapshot_sha256",
]


def parse(html: bytes, fetched_at: str, digest: str) -> list[dict[str, str]]:
    soup = BeautifulSoup(html.decode("utf-8"), "html.parser")
    heading = soup.find(string=lambda value: value and "هزینه انبارداری روزانه" in value)
    if heading is None:
        raise ValueError("IME schema changed: daily warehouse-fee heading was not found")
    table = heading.find_parent("table")
    if table is None:
        raise ValueError("IME schema changed: fee table was not found")
    rows = []
    for tr in table.find_all("tr")[1:]:
        cells = [" ".join(cell.stripped_strings) for cell in tr.find_all(["td", "th"])]
        if len(cells) != 3:
            raise ValueError(f"Unexpected IME fee row: {cells!r}")
        rows.append(dict(zip(COLUMNS, cells + [SOURCE_URL, fetched_at, digest], strict=True)))
    if len(rows) < 5:
        raise ValueError(f"Suspiciously short IME fee table: {len(rows)} rows")
    return rows


def collect(project_dir: Path, timeout: int = 60) -> Path:
    response = requests.get(SOURCE_URL, timeout=timeout)
    response.raise_for_status()
    raw = response.content
    fetched_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    digest = hashlib.sha256(raw).hexdigest()
    raw_dir = project_dir / "data" / "raw" / "warehouse_fees"
    snapshots = raw_dir / "snapshots"
    snapshots.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    snapshot = snapshots / f"WarehousesFee_{stamp}_{digest[:12]}.html"
    snapshot.write_bytes(raw)
    rows = parse(raw, fetched_at, digest)
    output = raw_dir / "ime_current_warehouse_fees.csv"
    temporary = output.with_suffix(".csv.tmp")
    with temporary.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=COLUMNS)
        writer.writeheader()
        writer.writerows(rows)
    temporary.replace(output)
    print(f"Saved {len(rows)} current fees to {output}")
    print(f"Immutable source snapshot: {snapshot}")
    return output


if __name__ == "__main__":
    collect(Path(__file__).resolve().parents[2])
