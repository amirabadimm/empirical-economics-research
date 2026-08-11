"""Incrementally collect Westmetall LME copper data.

The first run downloads every available year (2008 onward). Later runs start at
the year containing the newest locally stored observation, so the full history
is not downloaded again while revisions and newly published rows are captured.
"""

from __future__ import annotations

import argparse
import csv
import random
import re
import sys
import time
from datetime import date, datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


BASE_URL = "https://www.westmetall.com/en/markdaten.php"
FIRST_AVAILABLE_YEAR = 2008
FIELD = "LME_Cu_cash"
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


class TableRowParser(HTMLParser):
    """Extract text cells from HTML table rows using only the standard library."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.rows: list[list[str]] = []
        self._in_row = False
        self._cell_depth = 0
        self._cells: list[str] = []
        self._text: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag = tag.lower()
        if tag == "tr":
            self._in_row = True
            self._cells = []
        elif self._in_row and tag in {"td", "th"}:
            self._cell_depth += 1
            self._text = []

    def handle_data(self, data: str) -> None:
        if self._in_row and self._cell_depth:
            self._text.append(data)

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if self._in_row and tag in {"td", "th"} and self._cell_depth:
            value = " ".join("".join(self._text).split())
            self._cells.append(value)
            self._cell_depth -= 1
            self._text = []
        elif tag == "tr" and self._in_row:
            if self._cells:
                self.rows.append(self._cells)
            self._in_row = False
            self._cell_depth = 0


def build_url(year: int) -> str:
    query = urlencode({"action": "table", "field": FIELD, "year": year})
    return f"{BASE_URL}?{query}"


def download(url: str, timeout: int, retries: int) -> bytes:
    request = Request(
        url,
        headers={
            "User-Agent": "CopperResearchCollector/1.0 (weekly; polite single-page requests)",
            "Accept": "text/html,application/xhtml+xml",
        },
    )
    for attempt in range(1, retries + 1):
        try:
            with urlopen(request, timeout=timeout) as response:
                if response.status != 200:
                    raise RuntimeError(f"Unexpected HTTP status {response.status} for {url}")
                return response.read()
        except (HTTPError, URLError, TimeoutError) as exc:
            if attempt == retries:
                raise RuntimeError(f"Download failed after {retries} attempts: {url}") from exc
            wait_seconds = 2 ** (attempt - 1) + random.random()
            print(f"  attempt {attempt} failed; retrying in {wait_seconds:.1f}s", file=sys.stderr)
            time.sleep(wait_seconds)
    raise AssertionError("unreachable")


def parse_page(html: bytes, year: int, fetched_at: str, url: str) -> list[dict[str, str]]:
    parser = TableRowParser()
    parser.feed(html.decode("utf-8", errors="replace"))
    records: list[dict[str, str]] = []

    for cells in parser.rows:
        if len(cells) < 4 or not DATE_PATTERN.fullmatch(cells[0]):
            continue
        parsed_date = datetime.strptime(cells[0], "%d. %B %Y").date()
        if parsed_date.year != year:
            raise ValueError(f"Page for {year} contained unexpected date {parsed_date}")
        records.append(
            {
                "date": parsed_date.isoformat(),
                "cash_settlement": cells[1],
                "three_month": cells[2],
                "stock": cells[3],
                "source_year": str(year),
                "fetched_at_utc": fetched_at,
                "source_url": url,
            }
        )

    if not records:
        raise ValueError(f"No copper data rows found on the page for {year}; site layout may have changed")
    if len({row["date"] for row in records}) != len(records):
        raise ValueError(f"Duplicate dates were returned on the page for {year}")
    return records


def read_existing(csv_path: Path) -> dict[str, dict[str, str]]:
    if not csv_path.exists():
        return {}
    with csv_path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames != OUTPUT_COLUMNS:
            raise ValueError(f"Unexpected columns in {csv_path}: {reader.fieldnames}")
        return {row["date"]: row for row in reader}


def write_csv_safely(csv_path: Path, records: dict[str, dict[str, str]]) -> None:
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = csv_path.with_suffix(csv_path.suffix + ".tmp")
    with temporary_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=OUTPUT_COLUMNS)
        writer.writeheader()
        writer.writerows(records[key] for key in sorted(records))
    temporary_path.replace(csv_path)


def collect(project_dir: Path, timeout: int, retries: int, delay: float) -> None:
    raw_dir = project_dir / "data" / "raw" / "lme"
    snapshot_dir = raw_dir / "html_snapshots"
    csv_path = raw_dir / "copper_lme_raw.csv"
    existing = read_existing(csv_path)
    current_year = date.today().year
    newest_date = max(existing) if existing else None
    start_year = max(int(newest_date[:4]) if newest_date else FIRST_AVAILABLE_YEAR, FIRST_AVAILABLE_YEAR)
    if start_year > current_year:
        raise ValueError(f"Newest local year {start_year} is later than system year {current_year}")

    years = list(range(start_year, current_year + 1))
    print(f"Existing rows: {len(existing):,}")
    print(f"Fetching years: {years[0]}-{years[-1]}")
    fetched_records: dict[str, dict[str, str]] = {}

    for index, year in enumerate(years):
        url = build_url(year)
        print(f"Downloading {year}: {url}")
        html = download(url, timeout=timeout, retries=retries)
        fetched_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
        snapshot_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        (snapshot_dir / f"copper_{year}_{timestamp}.html").write_bytes(html)
        rows = parse_page(html, year, fetched_at, url)
        fetched_records.update({row["date"]: row for row in rows})
        print(f"  parsed {len(rows):,} rows")
        if index < len(years) - 1:
            time.sleep(delay)

    merged = existing | fetched_records
    new_dates = set(fetched_records) - set(existing)
    revised_dates = {
        key
        for key in set(fetched_records) & set(existing)
        if any(fetched_records[key][column] != existing[key][column] for column in OUTPUT_COLUMNS[1:4])
    }
    write_csv_safely(csv_path, merged)
    print(f"Saved {len(merged):,} rows to {csv_path}")
    print(f"New rows: {len(new_dates):,}; revised rows: {len(revised_dates):,}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--timeout", type=int, default=30, help="HTTP timeout in seconds")
    parser.add_argument("--retries", type=int, default=3, help="download attempts per page")
    parser.add_argument("--delay", type=float, default=1.0, help="seconds between yearly requests")
    args = parser.parse_args()
    collect(Path(__file__).resolve().parents[3], args.timeout, args.retries, args.delay)


if __name__ == "__main__":
    main()
