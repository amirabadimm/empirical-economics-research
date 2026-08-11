"""Snapshot selected historical IME warehouse-fee pages from Wayback."""

from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from pathlib import Path

import requests

CDX_URL = (
    "https://web.archive.org/cdx/search/cdx?url=www.ime.co.ir/"
    "hazine-anbardari.html&output=json&filter=statuscode:200&filter=mimetype:text/html"
    "&fl=timestamp,original,digest&collapse=digest"
)


def collect(project_dir: Path, timeout: int = 60) -> Path:
    response = requests.get(CDX_URL, timeout=timeout)
    response.raise_for_status()
    rows = response.json()
    if len(rows) < 2 or rows[0] != ["timestamp", "original", "digest"]:
        raise ValueError("Unexpected Wayback CDX response")
    raw_dir = project_dir / "data" / "raw" / "warehouse_fees" / "wayback"
    raw_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    digest = hashlib.sha256(response.content).hexdigest()
    output = raw_dir / f"cdx_{stamp}_{digest[:12]}.json"
    output.write_bytes(response.content)
    print(f"Saved {len(rows) - 1} unique archived-page records to {output}")
    return output


if __name__ == "__main__":
    collect(Path(__file__).resolve().parents[2])
