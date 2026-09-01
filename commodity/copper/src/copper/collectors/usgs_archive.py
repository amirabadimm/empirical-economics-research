"""Archive official USGS monthly copper Mineral Industry Survey workbooks."""

from __future__ import annotations

import argparse
import csv
import hashlib
import time
import urllib.parse
from datetime import datetime, timezone
from pathlib import Path

import requests
import truststore
from bs4 import BeautifulSoup


PROJECT_DIR = Path(__file__).resolve().parents[3]
SOURCE_DIR = PROJECT_DIR / "data" / "raw" / "global_market" / "usgs_mis"
LEGACY_URL = "https://apps.usgs.gov/minerals-information-archives/copper/mis/"
CURRENT_URL = (
    "https://www.usgs.gov/centers/national-minerals-information-center/"
    "copper-statistics-and-information"
)


def sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def discover(session: requests.Session, timeout: int) -> tuple[list[str], list[bytes]]:
    urls: set[str] = set()
    pages: list[bytes] = []
    for page_url in (LEGACY_URL, CURRENT_URL):
        response = session.get(page_url, timeout=timeout)
        response.raise_for_status()
        pages.append(response.content)
        soup = BeautifulSoup(response.content, "html.parser")
        for anchor in soup.find_all("a", href=True):
            url = urllib.parse.urljoin(page_url, anchor["href"])
            name = urllib.parse.urlparse(url).path.lower()
            if "/mis-" in name and "coppe" in name and name.endswith((".xls", ".xlsx")):
                urls.add(url)
    return sorted(urls), pages


def collect(timeout: int, delay: float) -> tuple[Path, int]:
    truststore.inject_into_ssl()
    session = requests.Session()
    session.headers["User-Agent"] = "empirical-economics-research copper collector/1.0"
    urls, pages = discover(session, timeout)
    SOURCE_DIR.mkdir(parents=True, exist_ok=True)
    snapshots = SOURCE_DIR / "snapshots"
    workbooks = SOURCE_DIR / "workbooks"
    snapshots.mkdir(exist_ok=True)
    workbooks.mkdir(exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    for index, payload in enumerate(pages):
        with (snapshots / f"source_index_{index}_{stamp}.html").open("xb") as handle:
            handle.write(payload)
    rows: list[dict] = []
    for index, url in enumerate(urls, start=1):
        filename = Path(urllib.parse.urlparse(url).path).name
        destination = workbooks / filename
        if destination.exists():
            payload = destination.read_bytes()
            status = "existing"
        else:
            response = session.get(url, timeout=timeout)
            response.raise_for_status()
            payload = response.content
            if len(payload) < 5_000 or payload[:2] not in {b"PK", b"\xd0\xcf"}:
                raise RuntimeError(f"Invalid workbook payload: {url}")
            with destination.open("xb") as handle:
                handle.write(payload)
            status = "downloaded"
            time.sleep(delay)
        rows.append({
            "filename": filename,
            "source_url": url,
            "bytes": len(payload),
            "sha256": sha256(payload),
            "status": status,
            "checked_at_utc": datetime.now(timezone.utc).isoformat(),
        })
        if index % 25 == 0:
            print(f"usgs: checked {index}/{len(urls)} workbooks", flush=True)
    manifest = SOURCE_DIR / "usgs_copper_mis_manifest.csv"
    temporary = manifest.with_suffix(".csv.tmp")
    with temporary.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    temporary.replace(manifest)
    return manifest, len(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--timeout", type=int, default=120)
    parser.add_argument("--delay", type=float, default=0.1)
    args = parser.parse_args()
    path, count = collect(args.timeout, args.delay)
    print(f"usgs: {count:,} workbooks -> {path}")


if __name__ == "__main__":
    main()
