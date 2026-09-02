"""Archive official CME metals bulletins and extract COMEX copper aggregate activity."""

from __future__ import annotations

import argparse
import csv
import io
import re
import time
from pathlib import Path

import requests
import truststore
from pypdf import PdfReader


PROJECT_DIR = Path(__file__).resolve().parents[3]
SOURCE_DIR = PROJECT_DIR / "data" / "raw" / "global_market" / "cme"
CDX_URL = "https://web.archive.org/cdx/search/cdx"
BULLETIN_URL = "www.cmegroup.com/daily_bulletin/current/Section62_Metals_Futures_Products.pdf"


def capture_index(session: requests.Session, timeout: int) -> list[dict]:
    response = session.get(CDX_URL, params={
        "url": BULLETIN_URL,
        "output": "json",
        "filter": "statuscode:200",
        "fl": "timestamp,original,statuscode,mimetype,digest,length",
        "collapse": "digest",
    }, timeout=timeout)
    response.raise_for_status()
    document = response.json()
    return [dict(zip(document[0], row)) for row in document[1:]]


def parse_bulletin(payload: bytes) -> dict:
    text = "\n".join(page.extract_text() or "" for page in PdfReader(io.BytesIO(payload)).pages)
    date_match = re.search(r"PG62\s+\w{3},\s+([A-Z][a-z]{2} \d{1,2}, \d{4})", text)
    section_match = re.search(r"HG FUT COMEX COPPER FUTURES", text)
    if not date_match or not section_match:
        raise RuntimeError("missing bulletin date or HG FUT section")
    legacy_total_match = re.search(
        r"(\d+)TOTAL\s+HG FUT\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s*([+-])", text
    )
    total_match = re.search(
        r"(\d+)TOTAL\s+HG FUT\s+(\d+)\s+(?:(\d+)\s+)?(\d+)([+-])", text
    )
    zero_volume_match = re.search(r"TOTAL\s+HG FUT\s+(\d+)\s+(\d+)([+-])", text)
    if legacy_total_match:
        globex_volume = int(legacy_total_match.group(1))
        open_outcry_volume = int(legacy_total_match.group(2))
        open_interest = int(legacy_total_match.group(3))
        pnt_pit_volume = int(legacy_total_match.group(4))
        change = int(legacy_total_match.group(5))
        sign = legacy_total_match.group(6)
    elif not total_match:
        if not zero_volume_match:
            raise RuntimeError("missing HG FUT aggregate volume/open-interest row")
        globex_volume, open_outcry_volume, pnt_pit_volume = 0, 0, 0
        open_interest = int(zero_volume_match.group(1))
        change = int(zero_volume_match.group(2))
        sign = zero_volume_match.group(3)
    else:
        globex_volume = int(total_match.group(1))
        open_outcry_volume = 0
        open_interest = int(total_match.group(2))
        pnt_pit_volume = int(total_match.group(3) or 0)
        change = int(total_match.group(4))
        sign = total_match.group(5)
    if sign == "-":
        change *= -1
    return {
        "trade_date": __import__("pandas").to_datetime(date_match.group(1)).date().isoformat(),
        "globex_volume_contracts": globex_volume,
        "open_outcry_volume_contracts": open_outcry_volume,
        "pnt_pit_volume_contracts": pnt_pit_volume,
        "futures_volume_contracts": globex_volume + open_outcry_volume + pnt_pit_volume,
        "open_interest_contracts": open_interest,
        "open_interest_change_contracts": change,
    }


def download(session: requests.Session, url: str, timeout: int) -> bytes:
    last_error: Exception | None = None
    for attempt in range(5):
        try:
            response = session.get(url, timeout=timeout)
            response.raise_for_status()
            if not response.content.startswith(b"%PDF"):
                raise RuntimeError("response is not PDF")
            return response.content
        except (requests.RequestException, RuntimeError) as error:
            last_error = error
            if attempt < 4:
                time.sleep(2 ** attempt)
    raise RuntimeError(f"failed to download {url}") from last_error


def collect(timeout: int, delay: float) -> tuple[Path, int]:
    truststore.inject_into_ssl()
    session = requests.Session()
    session.headers["User-Agent"] = "Mozilla/5.0 empirical-economics-research"
    SOURCE_DIR.mkdir(parents=True, exist_ok=True)
    snapshots = SOURCE_DIR / "bulletin_snapshots"
    snapshots.mkdir(exist_ok=True)
    captures = capture_index(session, timeout)
    manifest_rows: list[dict] = []
    observations: list[dict] = []
    for index, capture in enumerate(captures, start=1):
        timestamp = capture["timestamp"]
        replay_url = f"https://web.archive.org/web/{timestamp}id_/{capture['original']}"
        snapshot = snapshots / f"cme_metals_bulletin_{timestamp}.pdf"
        payload = snapshot.read_bytes() if snapshot.exists() else download(session, replay_url, timeout)
        if not snapshot.exists():
            with snapshot.open("xb") as handle:
                handle.write(payload)
            time.sleep(delay)
        error = ""
        try:
            row = parse_bulletin(payload) | {
                "archive_capture_utc": timestamp,
                "original_source_url": capture["original"],
                "replay_url": replay_url,
            }
            observations.append(row)
        except Exception as exc:
            error = f"{type(exc).__name__}: {exc}"
        manifest_rows.append(capture | {"replay_url": replay_url, "snapshot": snapshot.name, "parse_error": error})
        if index % 20 == 0:
            print(f"cme bulletins: processed {index}/{len(captures)} captures", flush=True)
    manifest = SOURCE_DIR / "cme_metals_bulletin_capture_manifest.csv"
    with manifest.with_suffix(".csv.tmp").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(manifest_rows[0]))
        writer.writeheader()
        writer.writerows(manifest_rows)
    manifest.with_suffix(".csv.tmp").replace(manifest)
    errors = [row for row in manifest_rows if row["parse_error"]]
    if errors:
        raise RuntimeError(f"{len(errors)} CME bulletins failed parsing; see {manifest}")
    latest = {}
    for row in observations:
        if row["trade_date"] not in latest or row["archive_capture_utc"] > latest[row["trade_date"]]["archive_capture_utc"]:
            latest[row["trade_date"]] = row
    rows = sorted(latest.values(), key=lambda row: row["trade_date"])
    output = SOURCE_DIR / "comex_copper_daily_activity_raw.csv"
    with output.with_suffix(".csv.tmp").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    output.with_suffix(".csv.tmp").replace(output)
    print(f"cme bulletins: {len(captures)} official PDFs; {len(rows)} unique trade dates")
    return output, len(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--timeout", type=int, default=120)
    parser.add_argument("--delay", type=float, default=0.15)
    args = parser.parse_args()
    path, count = collect(args.timeout, args.delay)
    print(f"cme bulletins: {count:,} rows -> {path}")


if __name__ == "__main__":
    main()
