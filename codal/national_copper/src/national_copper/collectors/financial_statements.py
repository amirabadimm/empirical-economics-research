"""Collect National Copper cumulative financial statements from public Codal endpoints."""

from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import json
import os
import re
import subprocess
import tempfile
from datetime import UTC, datetime
from pathlib import Path
from urllib.parse import urlencode, urljoin


PROJECT_ROOT = Path(__file__).resolve().parents[3]
RAW_DIR = PROJECT_ROOT / "data" / "raw" / "financial_statements"
API_SNAPSHOTS = RAW_DIR / "api_snapshots"
EXCEL_SNAPSHOTS = RAW_DIR / "excel_snapshots"
REPORT_SNAPSHOTS = RAW_DIR / "report_snapshots"
INDEX_PATH = RAW_DIR / "filing_index.csv"
Q1_INDEX_PATH = RAW_DIR / "q1_filing_index.csv"

SEARCH_URL = "https://search.codal.ir/api/search/v2/q"
SYMBOL = "فملی"
COMPANY = "ملی صنایع مس ایران"
LETTER_TYPE = 6

PERSIAN_DIGITS = str.maketrans("۰۱۲۳۴۵۶۷۸۹", "0123456789")
PERIOD_RE = re.compile(r"منتهی\s*به\s*(1[34]\d{2}/\d{2}/\d{2})")
MONTH_RE = re.compile(r"دوره\s*([۳۶۹369])\s*ماهه")


def normalize_text(value: object) -> str:
    return " ".join(str(value or "").replace("ي", "ی").replace("ك", "ک").split())


def period_end(title: str) -> str:
    match = PERIOD_RE.search(normalize_text(title).translate(PERSIAN_DIGITS))
    if not match:
        raise ValueError(f"Cannot identify period end from title: {title!r}")
    return match.group(1)


def statement_months(title: str) -> int:
    normalized = normalize_text(title)
    match = MONTH_RE.search(normalized)
    if match:
        return int(match.group(1).translate(PERSIAN_DIGITS))
    if "سال مالی" in normalized and "صورت" in normalized and "مالی" in normalized:
        return 12
    raise ValueError(f"Not a supported financial-statement period: {title!r}")


def is_parent_financial_filing(letter: dict[str, object]) -> bool:
    title = normalize_text(letter.get("Title"))
    identity_and_type = (
        normalize_text(letter.get("Symbol")) == SYMBOL
        and normalize_text(letter.get("CompanyName")) == COMPANY
        and "صورت" in title
        and "مالی" in title
    )
    if not identity_and_type:
        return False
    try:
        months = statement_months(title)
        return months in {3, 6, 9, 12} and (months == 12 or "تلفیقی" not in title)
    except ValueError:
        return False


def is_q1_parent_filing(letter: dict[str, object]) -> bool:
    return is_parent_financial_filing(letter) and statement_months(str(letter.get("Title"))) == 3


def fetch(url: str) -> bytes:
    command = [
        "curl.exe",
        "--http1.1",
        "--compressed",
        "--location",
        "--silent",
        "--show-error",
        "--fail",
        "--retry",
        "3",
        "--retry-all-errors",
        "--connect-timeout",
        "30",
        "--max-time",
        "60",
        "--user-agent",
        "Mozilla/5.0 (Codal research collector)",
        url,
    ]
    return subprocess.run(command, check=True, capture_output=True).stdout


def request_json(params: dict[str, object]) -> tuple[dict, bytes]:
    raw = fetch(f"{SEARCH_URL}?{urlencode(params)}")
    payload = json.loads(raw)
    if payload.get("IsAttacker"):
        raise RuntimeError("Codal rejected the request as automated traffic")
    return payload, raw


def write_immutable(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        if path.read_bytes() != content:
            raise RuntimeError(f"Immutable snapshot collision: {path}")
        return
    path.write_bytes(content)


def atomic_csv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    handle, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(handle, "w", newline="", encoding="utf-8-sig") as stream:
            writer = csv.DictWriter(stream, fieldnames=fields)
            writer.writeheader()
            writer.writerows(rows)
        os.replace(temporary_name, path)
    except Exception:
        Path(temporary_name).unlink(missing_ok=True)
        raise


def collect() -> list[dict[str, object]]:
    retrieved = datetime.now(UTC)
    stamp = retrieved.strftime("%Y%m%dT%H%M%SZ")
    params: dict[str, object] = {
        "PageNumber": 1,
        "Symbol": SYMBOL,
        "LetterType": LETTER_TYPE,
        "Category": 1,
        "FromDate": "1380/01/01",
        "Audited": "true",
        "NotAudited": "true",
        "Consolidatable": "true",
        "NotConsolidatable": "true",
        "Childs": "false",
        "Mains": "true",
        "Publisher": "false",
        "search": "true",
    }

    first, raw = request_json(params)
    pages = int(first["Page"])
    payloads = [(1, first, raw)]
    for page in range(2, pages + 1):
        params["PageNumber"] = page
        payload, page_raw = request_json(params)
        if int(payload["Total"]) != int(first["Total"]):
            raise RuntimeError("Codal result count changed during pagination")
        payloads.append((page, payload, page_raw))

    all_letters: list[dict[str, object]] = []
    for page, payload, page_raw in payloads:
        digest = hashlib.sha256(page_raw).hexdigest()
        snapshot = API_SNAPSHOTS / f"search_page_{page}_{stamp}_{digest[:12]}.json.gz"
        write_immutable(snapshot, gzip.compress(page_raw, mtime=0))
        all_letters.extend(payload["Letters"])

    candidates = [letter for letter in all_letters if is_parent_financial_filing(letter)]
    if not candidates:
        raise RuntimeError("No exact-company, non-consolidated three-month filings found")

    rows: list[dict[str, object]] = []
    for letter in candidates:
        if not letter.get("HasExcel") or not letter.get("ExcelUrl"):
            raise RuntimeError(f"Filing {letter.get('TracingNo')} has no Excel export")
        tracing_no = int(letter["TracingNo"])
        existing = sorted(EXCEL_SNAPSHOTS.glob(f"{tracing_no}_*.*"))
        if len(existing) > 1:
            raise RuntimeError(f"Multiple snapshots found for tracing number {tracing_no}")
        content = existing[0].read_bytes() if existing else fetch(str(letter["ExcelUrl"]))
        prefix = content[:1000].lower()
        if b"<html" in prefix:
            extension = "html"
        elif content.startswith(b"PK\x03\x04"):
            extension = "xlsx"
        elif content.startswith(b"\xd0\xcf\x11\xe0"):
            extension = "xls"
        else:
            raise RuntimeError(
                f"Unexpected Excel-export format for {letter.get('TracingNo')}: {content[:80]!r}"
            )
        digest = hashlib.sha256(content).hexdigest()
        excel_snapshot = EXCEL_SNAPSHOTS / f"{tracing_no}_{digest[:16]}.{extension}"
        write_immutable(excel_snapshot, content)
        snapshot = excel_snapshot
        snapshot_kind = "excel_export"
        if extension == "html" and len(content) < 50_000:
            report_content = fetch(urljoin("https://codal.ir", str(letter["Url"])))
            if b"var datasource =" not in report_content:
                raise RuntimeError(f"Fallback report has no structured datasource for {tracing_no}")
            report_digest = hashlib.sha256(report_content).hexdigest()
            snapshot = REPORT_SNAPSHOTS / f"{tracing_no}_{report_digest[:16]}.html"
            write_immutable(snapshot, report_content)
            digest = report_digest
            snapshot_kind = "report_html_fallback"
        title = str(letter["Title"])
        rows.append(
            {
                "period_end_jalali": period_end(title),
                "statement_months": statement_months(title),
                "tracing_no": tracing_no,
                "symbol": letter["Symbol"],
                "company_name": letter["CompanyName"],
                "title": title,
                "is_correction": "اصلاحیه" in normalize_text(title),
                "publish_datetime_jalali": letter["PublishDateTime"],
                "sent_datetime_jalali": letter["SentDateTime"],
                "has_html": bool(letter["HasHtml"]),
                "has_pdf": bool(letter["HasPdf"]),
                "has_attachment": bool(letter["HasAttachment"]),
                "report_url": urljoin("https://codal.ir", str(letter["Url"])),
                "excel_url": letter["ExcelUrl"],
                "pdf_url": urljoin("https://codal.ir", str(letter["PdfUrl"])),
                "snapshot_path": snapshot.relative_to(PROJECT_ROOT).as_posix(),
                "snapshot_sha256": digest,
                "snapshot_kind": snapshot_kind,
                "excel_snapshot_path": excel_snapshot.relative_to(PROJECT_ROOT).as_posix(),
                "retrieved_at_utc": retrieved.isoformat(),
            }
        )

    rows.sort(key=lambda row: (str(row["period_end_jalali"]), str(row["publish_datetime_jalali"])))
    fields = list(rows[0])
    atomic_csv(INDEX_PATH, rows, fields)
    atomic_csv(Q1_INDEX_PATH, [row for row in rows if row["statement_months"] == 3], fields)
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args()
    rows = collect()
    periods = {row["period_end_jalali"] for row in rows}
    print(f"Collected {len(rows)} filings across {len(periods)} statement periods")


if __name__ == "__main__":
    main()
