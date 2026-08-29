"""Shared incremental Westmetall/LME collector with explicit metal configuration."""

from __future__ import annotations

import csv
import random
import re
import time
from dataclasses import dataclass
from datetime import date, datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

BASE_URL = "https://www.westmetall.com/en/markdaten.php"
FIRST_AVAILABLE_YEAR = 2008
OUTPUT_COLUMNS = [
    "date",
    "cash_settlement",
    "three_month",
    "stock",
    "source_year",
    "fetched_at_utc",
    "source_url",
]
DATE_PATTERN = re.compile(r"^\d{1,2}\.\s+[A-Za-z]+\s+\d{4}$")


@dataclass(frozen=True)
class LmeConfig:
    slug: str
    field: str
    csv_name: str


class TableRowParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.rows = []
        self.in_row = False
        self.depth = 0
        self.cells = []
        self.text = []

    def handle_starttag(self, tag, attrs) -> None:
        if tag == "tr":
            self.in_row = True
            self.cells = []
        elif self.in_row and tag in {"td", "th"}:
            self.depth += 1
            self.text = []

    def handle_data(self, data: str) -> None:
        if self.in_row and self.depth:
            self.text.append(data)

    def handle_endtag(self, tag: str) -> None:
        if self.in_row and tag in {"td", "th"} and self.depth:
            self.cells.append(" ".join("".join(self.text).split()))
            self.depth -= 1
            self.text = []
        elif tag == "tr" and self.in_row:
            if self.cells:
                self.rows.append(self.cells)
            self.in_row = False
            self.depth = 0


def build_url(config: LmeConfig, year: int) -> str:
    return f"{BASE_URL}?{urlencode({'action': 'table', 'field': config.field, 'year': year})}"


def download(url: str, user_agent: str, timeout: int, retries: int) -> bytes:
    request = Request(
        url, headers={"User-Agent": user_agent, "Accept": "text/html,application/xhtml+xml"}
    )
    for attempt in range(1, retries + 1):
        try:
            with urlopen(request, timeout=timeout) as response:
                if response.status != 200:
                    raise RuntimeError(f"Unexpected HTTP status {response.status}")
                return response.read()
        except (HTTPError, URLError, TimeoutError) as exc:
            if attempt == retries:
                raise RuntimeError(f"Download failed: {url}") from exc
            time.sleep(2 ** (attempt - 1) + random.random())
    raise AssertionError("unreachable")


def parse_page(
    html: bytes, config: LmeConfig, year: int, fetched_at: str, url: str
) -> list[dict[str, str]]:
    parser = TableRowParser()
    parser.feed(html.decode("utf-8", errors="replace"))
    records = []
    for cells in parser.rows:
        if len(cells) < 4 or not DATE_PATTERN.fullmatch(cells[0]):
            continue
        parsed = datetime.strptime(cells[0], "%d. %B %Y").date()
        if parsed.year != year:
            raise ValueError(f"Unexpected date {parsed} on {year} page")
        records.append(
            {
                "date": parsed.isoformat(),
                "cash_settlement": cells[1],
                "three_month": cells[2],
                "stock": cells[3],
                "source_year": str(year),
                "fetched_at_utc": fetched_at,
                "source_url": url,
            }
        )
    if not records:
        raise ValueError(f"No {config.slug} rows found for {year}")
    if len(records) != len({row["date"] for row in records}):
        raise ValueError(f"Duplicate dates for {year}")
    return records


def read_existing(path: Path) -> dict[str, dict[str, str]]:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames != OUTPUT_COLUMNS:
            raise ValueError(f"Unexpected columns in {path}")
        rows = list(reader)
    dates = [row["date"] for row in rows]
    if len(dates) != len(set(dates)) or dates != sorted(dates):
        raise ValueError(f"Dates not unique/sorted: {path}")
    return {row["date"]: row for row in rows}


def archive_html(path: Path, html: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as handle:
        handle.write(html)


def write_atomic(path: Path, records: dict[str, dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=OUTPUT_COLUMNS)
        writer.writeheader()
        writer.writerows(records[key] for key in sorted(records))
    temporary.replace(path)


def collect(project_dir: Path, config: LmeConfig, timeout: int, retries: int, delay: float) -> Path:
    raw_dir = project_dir / "data" / "raw" / "lme"
    csv_path = raw_dir / config.csv_name
    existing = read_existing(csv_path)
    current = date.today().year
    start = max(int(max(existing)[:4]) if existing else FIRST_AVAILABLE_YEAR, FIRST_AVAILABLE_YEAR)
    if start > current:
        raise ValueError(f"Newest local year {start} exceeds system year {current}")
    fetched = {}
    years = list(range(start, current + 1))
    for index, year in enumerate(years):
        url = build_url(config, year)
        html = download(url, f"EmpiricalEconomicsResearch/{config.slug}", timeout, retries)
        fetched_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        archive_html(raw_dir / "html_snapshots" / f"{config.slug}_{year}_{stamp}.html", html)
        fetched.update(
            {row["date"]: row for row in parse_page(html, config, year, fetched_at, url)}
        )
        if index < len(years) - 1:
            time.sleep(delay)
    write_atomic(csv_path, existing | fetched)
    return csv_path
