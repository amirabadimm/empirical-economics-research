"""Collect verified scanned statements from Codal's legacy OldLetters archive."""

from __future__ import annotations

import csv
import hashlib
import os
import subprocess
import tempfile
from datetime import UTC, datetime
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
RAW_DIR = PROJECT_ROOT / "data" / "raw" / "financial_statements"
SNAPSHOT_DIR = RAW_DIR / "legacy_pdf_snapshots"
INDEX_PATH = RAW_DIR / "legacy_filing_index.csv"

FILINGS = (
    {
        "period_end_jalali": "1386/06/31",
        "statement_months": 6,
        "published": "1386/07/30 17:49:00",
        "archive_id": "nTT9Aq2idAGGl3OYjUTmDQ%3d%3d",
        "filename": "860703005.pdf",
        "sha256": "3751e5ce363cfe38ad85713662fb4140cb25c3777b772d16cb599ad41557bf1d",
        "revenue": 10_239_107,
        "gross_profit": 6_374_149,
        "net_profit": 4_707_683,
        "statement_page": 3,
    },
    {
        "period_end_jalali": "1386/09/30",
        "statement_months": 9,
        "published": "1386/10/27 01:36:46",
        "archive_id": "ZPYuL7a7heeW91HdwisHzA%3d%3d",
        "filename": "861026-8.pdf",
        "sha256": "11fe3f1c284562ec5956dc36fe311e077d3373075274ebadcfcc6857654a7d1e",
        "revenue": 15_156_071,
        "gross_profit": 9_399_486,
        "net_profit": 7_182_236,
        "statement_page": 3,
    },
)


def fetch(url: str) -> bytes:
    return subprocess.run(
        [
            "curl.exe", "--http1.1", "--compressed", "--location", "--silent",
            "--show-error", "--fail", "--retry", "3", "--retry-all-errors",
            "--max-time", "90", "--user-agent", "Mozilla/5.0 (Codal research collector)", url,
        ],
        check=True,
        capture_output=True,
    ).stdout


def atomic_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    handle, name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(handle, "w", newline="", encoding="utf-8-sig") as stream:
            writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)
        os.replace(name, path)
    except Exception:
        Path(name).unlink(missing_ok=True)
        raise


def collect() -> list[dict[str, object]]:
    retrieved = datetime.now(UTC).isoformat()
    rows = []
    for filing in FILINGS:
        url = f"https://www.codal.ir/OldLetters/DownloadFiles.ashx?ID={filing['archive_id']}"
        snapshot = SNAPSHOT_DIR / filing["filename"]
        content = snapshot.read_bytes() if snapshot.exists() else fetch(url)
        digest = hashlib.sha256(content).hexdigest()
        if digest != filing["sha256"]:
            raise RuntimeError(f"Legacy snapshot hash mismatch for {filing['filename']}: {digest}")
        snapshot.parent.mkdir(parents=True, exist_ok=True)
        if not snapshot.exists():
            snapshot.write_bytes(content)
        rows.append(
            {
                "period_end_jalali": filing["period_end_jalali"],
                "statement_months": filing["statement_months"],
                "symbol": "فملي",
                "company_name": "ملي صنايع مس ايران",
                "title": f"صورت‌های مالی میان‌دوره‌ای {filing['statement_months']} ماهه (حسابرسی نشده)",
                "publish_datetime_jalali": filing["published"],
                "audit_status": "حسابرسی نشده",
                "report_url": url,
                "snapshot_path": snapshot.relative_to(PROJECT_ROOT).as_posix(),
                "snapshot_sha256": digest,
                "snapshot_kind": "legacy_scanned_pdf_manual_double_check",
                "statement_page": filing["statement_page"],
                "operating_revenue_million_irr": filing["revenue"],
                "gross_profit_million_irr": filing["gross_profit"],
                "net_profit_million_irr": filing["net_profit"],
                "retrieved_at_utc": retrieved,
            }
        )
    atomic_csv(INDEX_PATH, rows)
    return rows


if __name__ == "__main__":
    print(f"Collected {len(collect())} verified legacy statements")
