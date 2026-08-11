"""Incrementally extend USD/IRR data using TGJU daily closing prices."""

from __future__ import annotations

import csv
import shutil
import subprocess
import time
from datetime import date, datetime, timezone
from decimal import Decimal, InvalidOperation
from html.parser import HTMLParser
from pathlib import Path


URL = "https://www.tgju.org/profile/price_dollar_rl/history"
COLUMNS = ["date_pr", "date_gr", "source", "price_irr", "price_method"]
LEGACY_COLUMNS = ["date_pr", "date_gr", "source", "price_avg"]


class HistoryParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.in_target_body = False
        self.in_row = False
        self.in_cell = False
        self.cell_parts: list[str] = []
        self.row: list[str] = []
        self.rows: list[list[str]] = []

    def handle_starttag(self, tag: str, attrs) -> None:
        attributes = dict(attrs)
        if tag == "tbody" and attributes.get("id") == "table-list":
            self.in_target_body = True
        elif self.in_target_body and tag == "tr":
            self.in_row = True
            self.row = []
        elif self.in_row and tag == "td":
            self.in_cell = True
            self.cell_parts = []

    def handle_data(self, data: str) -> None:
        if self.in_cell:
            self.cell_parts.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag == "td" and self.in_cell:
            self.row.append("".join(self.cell_parts).strip())
            self.in_cell = False
        elif tag == "tr" and self.in_row:
            if self.row:
                self.rows.append(self.row)
            self.in_row = False
        elif tag == "tbody" and self.in_target_body:
            self.in_target_body = False


def jalali_to_gregorian(jy: int, jm: int, jd: int) -> tuple[int, int, int]:
    jy += 1595
    days = -355668 + 365 * jy + (jy // 33) * 8 + ((jy % 33 + 3) // 4) + jd
    days += (jm - 1) * 31 if jm < 7 else 186 + (jm - 7) * 30
    gy = 400 * (days // 146097)
    days %= 146097
    if days > 36524:
        days -= 1
        gy += 100 * (days // 36524)
        days %= 36524
        if days >= 365:
            days += 1
    gy += 4 * (days // 1461)
    days %= 1461
    if days > 365:
        gy += (days - 1) // 365
        days = (days - 1) % 365
    gd = days + 1
    leap = gy % 4 == 0 and (gy % 100 != 0 or gy % 400 == 0)
    month_days = [31, 29 if leap else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    gm = 1
    for length in month_days:
        if gd <= length:
            break
        gd -= length
        gm += 1
    return gy, gm, gd


def canonical_dates(persian: str) -> tuple[str, str]:
    jy, jm, jd = map(int, persian.replace("-", "/").split("/"))
    gy, gm, gd = jalali_to_gregorian(jy, jm, jd)
    return f"{jy:04d}/{jm:02d}/{jd:02d}", f"{gy}/{gm}/{gd}"


def number(value: str) -> Decimal:
    try:
        return Decimal(value.replace(",", "").strip())
    except InvalidOperation as exc:
        raise ValueError(f"Invalid TGJU number: {value!r}") from exc


def formatted(value: Decimal) -> str:
    if value == value.to_integral_value():
        return f"{int(value):,}"
    return f"{value:,f}".rstrip("0").rstrip(".")


def download(timeout: int = 60, retries: int = 3) -> bytes:
    curl = shutil.which("curl.exe") or shutil.which("curl")
    if not curl:
        raise RuntimeError("curl was not found in PATH")
    command = [curl, "-4", "-L", "--tlsv1.2", "--silent", "--show-error",
               "--connect-timeout", "20", "--max-time", str(timeout),
               "--user-agent", "Mozilla/5.0", URL]
    error = ""
    for attempt in range(1, retries + 1):
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
        if result.returncode == 0 and result.stdout:
            return result.stdout
        error = result.stderr.decode("utf-8", errors="replace").strip()
        if attempt < retries:
            time.sleep(2 ** (attempt - 1))
    raise RuntimeError(f"TGJU download failed: {error}")


def parse_tgju(html: bytes) -> list[dict[str, str]]:
    parser = HistoryParser()
    parser.feed(html.decode("utf-8-sig", errors="strict"))
    output = []
    for cells in parser.rows:
        if len(cells) != 8:
            raise ValueError(f"Unexpected TGJU history row with {len(cells)} cells: {cells}")
        opening, low, high, closing, change, change_pct, gregorian, persian = cells
        date_pr, date_gr = canonical_dates(persian)
        page_gregorian = date.fromisoformat(gregorian.replace("/", "-"))
        expected_gregorian = date(*jalali_to_gregorian(*map(int, date_pr.split("/"))))
        if page_gregorian != expected_gregorian:
            raise ValueError(f"TGJU date mismatch: {date_pr} / {gregorian}")
        closing_price = number(closing)
        output.append({"date_pr": date_pr, "date_gr": date_gr,
                       "source": "tgju", "price_irr": formatted(closing_price),
                       "price_method": "close"})
    if not output:
        raise ValueError("TGJU history table was not found or was empty")
    return output


def update(project_dir: Path) -> None:
    csv_path = project_dir / "data" / "raw" / "fx" / "usd_to_rial.csv"
    with csv_path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames not in (COLUMNS, LEGACY_COLUMNS):
            raise ValueError(f"Unexpected CSV columns: {reader.fieldnames}")
        existing_rows = list(reader)
    if reader.fieldnames == LEGACY_COLUMNS:
        existing_rows = [
            {
                "date_pr": row["date_pr"],
                "date_gr": row["date_gr"],
                "source": row["source"],
                "price_irr": row["price_avg"],
                "price_method": "legacy_high_low_midpoint",
            }
            for row in existing_rows
        ]
    existing: dict[str, dict[str, str]] = {}
    identical_duplicates = 0
    for row in existing_rows:
        prior = existing.get(row["date_pr"])
        if prior is None:
            existing[row["date_pr"]] = row
        elif prior == row:
            identical_duplicates += 1
        else:
            raise ValueError(
                f"Conflicting rows for Persian date {row['date_pr']}: {prior} / {row}"
            )

    html = download()
    snapshots = project_dir / "data" / "raw" / "fx" / "usd_snapshots"
    snapshots.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    (snapshots / f"tgju_usd_history_{stamp}.html").write_bytes(html)
    fetched = {row["date_pr"]: row for row in parse_tgju(html)}

    corrections = 0
    for row in existing.values():
        date_pr, correct_date_gr = canonical_dates(row["date_pr"])
        if row["date_gr"] != correct_date_gr:
            row["date_gr"] = correct_date_gr
            corrections += 1
    new_dates = sorted(set(fetched) - set(existing))
    revised_dates = sorted(
        key for key in set(fetched) & set(existing)
        if existing[key] != fetched[key]
    )
    for key, row in fetched.items():
        existing[key] = row

    temporary = csv_path.with_suffix(csv_path.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=COLUMNS)
        writer.writeheader()
        writer.writerows(existing[key] for key in sorted(existing))
    temporary.replace(csv_path)
    print(f"Existing rows: {len(existing_rows)}")
    print(f"Identical duplicate rows removed: {identical_duplicates}")
    print(f"TGJU rows visible: {len(fetched)}")
    print(f"New rows added: {len(new_dates)}")
    print(f"Visible TGJU rows updated to close: {len(revised_dates)}")
    print(f"Gregorian dates corrected: {corrections}")
    print(f"Coverage: {min(existing)} through {max(existing)}")
    print(f"Output: {csv_path}")


if __name__ == "__main__":
    update(Path(__file__).resolve().parents[3])
