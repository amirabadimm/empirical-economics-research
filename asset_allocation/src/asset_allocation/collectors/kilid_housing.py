"""Incrementally archive Kilid Tehran monthly prices without revising old observations."""

from __future__ import annotations

import csv
import hashlib
import os
import re
import tempfile
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path
from zoneinfo import ZoneInfo

import jdatetime
import requests

ROOT = Path(__file__).resolve().parents[3]
URL = "https://kilid.com/house-prices/tehran"
SNAPSHOTS = ROOT / "data/raw/housing/kilid/snapshots"
ORIGINAL = SNAPSHOTS / "455cd4d7f670e77bd8a5928301d3e321b6e879157ac38b2beff9a4751755c807.html"
CANONICAL = ROOT / "data/raw/housing/kilid/tehran_monthly.csv"
FIELDS = ("jalali_period", "avg_price_million_irr_per_m2", "source_snapshot", "source_url")
MONTHS = {name: number for number, name in enumerate(
    ("فروردین", "اردیبهشت", "خرداد", "تیر", "مرداد", "شهریور", "مهر", "آبان", "آذر", "دی", "بهمن", "اسفند"), 1)}
DIGITS = str.maketrans("۰۱۲۳۴۵۶۷۸۹٫", "0123456789.")
PATTERN = re.compile(r'\\"children\\":\\"([^\\"]+ - 1[34]\d{2})\\".*?'
                     r'\\"children\\":\\"([^\\"]+ میلیون تومان)\\"')


def parse_snapshot(payload: bytes) -> dict[str, str]:
    text = payload.decode("utf-8-sig")
    result: dict[str, str] = {}
    for label, price_label in PATTERN.findall(text):
        month_name, year = (part.strip() for part in label.split("-"))
        period = f"{year}/{MONTHS[month_name]:02}"
        if period in result:
            raise ValueError(f"Duplicate Kilid month {period}")
        value = Decimal(price_label.split()[0].translate(DIGITS)) * 10
        if value <= 0:
            raise ValueError(f"Invalid Kilid price in {period}")
        result[period] = format(value, "f")
    if not result:
        raise ValueError("Kilid snapshot has no Tehran monthly prices")
    return result


def latest_complete_period(as_of: date) -> str:
    today = jdatetime.date.fromgregorian(date=as_of)
    year, month = (today.year - 1, 12) if today.month == 1 else (today.year, today.month - 1)
    return f"{year:04}/{month:02}"


def relative_snapshot(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def archive(payload: bytes) -> Path:
    SNAPSHOTS.mkdir(parents=True, exist_ok=True)
    path = SNAPSHOTS / (hashlib.sha256(payload).hexdigest() + ".html")
    if not path.exists():
        with tempfile.NamedTemporaryFile("wb", delete=False, dir=SNAPSHOTS, suffix=".tmp") as handle:
            handle.write(payload)
            temporary = Path(handle.name)
        os.replace(temporary, path)
    return path


def read_canonical() -> dict[str, dict[str, str]]:
    if not CANONICAL.exists():
        old = parse_snapshot(ORIGINAL.read_bytes())
        return {period: {"jalali_period": period, "avg_price_million_irr_per_m2": value,
                         "source_snapshot": relative_snapshot(ORIGINAL), "source_url": URL}
                for period, value in old.items()}
    with CANONICAL.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    result = {row["jalali_period"]: row for row in rows}
    if len(result) != len(rows):
        raise ValueError("Duplicate canonical Kilid month")
    return result


def merge(existing: dict[str, dict[str, str]], incoming: dict[str, str],
          snapshot: Path, as_of: date) -> dict[str, dict[str, str]]:
    complete = latest_complete_period(as_of)
    eligible = {period: value for period, value in incoming.items() if period <= complete}
    overlap = set(existing) & set(eligible)
    if len(overlap) < 3:
        raise ValueError("Insufficient Kilid overlap to validate a refresh")
    for period in overlap:
        if Decimal(existing[period]["avg_price_million_irr_per_m2"]) != Decimal(eligible[period]):
            raise ValueError(f"Kilid revised historical month {period}; review snapshots before updating")
    result = existing.copy()
    for period in sorted(set(eligible) - set(existing)):
        if period <= max(existing):
            raise ValueError(f"Kilid inserted historical month {period}; review before updating")
        result[period] = {"jalali_period": period, "avg_price_million_irr_per_m2": eligible[period],
                          "source_snapshot": relative_snapshot(snapshot), "source_url": URL}
    return result


def write_canonical(rows: dict[str, dict[str, str]]) -> None:
    CANONICAL.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", delete=False,
                                     dir=CANONICAL.parent, suffix=".tmp") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows[period] for period in sorted(rows))
        temporary = Path(handle.name)
    os.replace(temporary, CANONICAL)


def collect(as_of: date | None = None) -> dict[str, str | int]:
    as_of = as_of or datetime.now(ZoneInfo("Asia/Tehran")).date()
    response = requests.get(URL, headers={"User-Agent": "asset-allocation-research/0.1"}, timeout=60)
    response.raise_for_status()
    incoming = parse_snapshot(response.content)
    snapshot = archive(response.content)
    existing = read_canonical()
    merged = merge(existing, incoming, snapshot, as_of)
    if not CANONICAL.exists() or merged != existing:
        write_canonical(merged)
    return {"snapshot": relative_snapshot(snapshot), "months": len(merged),
            "new_months": len(merged) - len(existing), "latest_complete_period": max(merged)}


if __name__ == "__main__":
    print(collect())
