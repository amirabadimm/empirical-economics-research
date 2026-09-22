"""Fetch the complete official FRED CPIAUCNS history."""
import csv
import io
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from .io_utils import atomic_write
from .paths import RAW

SERIES = "CPIAUCNS"
API_URL = "https://api.stlouisfed.org/fred/series/observations"
CSV_URL = "https://fred.stlouisfed.org/graph/fredgraph.csv?id=CPIAUCNS"


def _download(url: str) -> bytes:
    request = Request(url, headers={"User-Agent": "economic-usd-research/1.0"})
    with urlopen(request, timeout=60) as response:
        return response.read()


def fetch() -> None:
    raw_dir = RAW / "us_cpi"
    raw_dir.mkdir(parents=True, exist_ok=True)
    key = os.getenv("FRED_API_KEY")
    retrieved = datetime.now(timezone.utc).isoformat()
    rows: list[dict[str, str]] = []
    if key:
        query = urlencode({"series_id": SERIES, "api_key": key, "file_type": "json", "observation_start": "1776-07-04"})
        content = _download(f"{API_URL}?{query}")
        (raw_dir / "CPIAUCNS_observations.json").write_bytes(content)
        payload = json.loads(content)
        for item in payload["observations"]:
            rows.append({"observation_date": item["date"], "CPIAUCNS": item["value"]})
        method = "FRED API"
    else:
        content = _download(CSV_URL)
        (raw_dir / "CPIAUCNS.csv").write_bytes(content)
        reader = csv.DictReader(io.StringIO(content.decode("utf-8-sig")))
        rows = [{"observation_date": r.get("DATE") or r.get("observation_date", ""), "CPIAUCNS": r[SERIES]} for r in reader]
        method = "official FRED CSV endpoint (FRED_API_KEY not set)"
    metadata = [{"series_id": SERIES, "title": "Consumer Price Index for All Urban Consumers: All Items in U.S. City Average", "seasonal_adjustment": "Not Seasonally Adjusted", "retrieved_at_utc": retrieved, "retrieval_method": method, "source_url": CSV_URL if not key else API_URL}]
    atomic_write(raw_dir / "retrieval_metadata.csv", list(metadata[0]), metadata)
    clean = []
    for row in rows:
        if row["CPIAUCNS"] in ("", "."):
            value = ""
        else:
            value = row["CPIAUCNS"]
        dt = datetime.strptime(row["observation_date"], "%Y-%m-%d").date()
        clean.append({"date": dt.isoformat(), "year": dt.year, "month": dt.month, "us_cpi": value, "unit": "index_1982_1984_100", "frequency": "monthly", "seasonal_adjustment": "not_seasonally_adjusted", "source": "FRED", "series_id": SERIES})
    clean.sort(key=lambda r: r["date"])
    atomic_write(PROCESSED / "us_cpi_urban_all_items.csv", list(clean[0]), clean)
    print(f"US CPI: {len(clean)} rows, {clean[0]['date']} through {clean[-1]['date']} ({method})")


from .paths import PROCESSED

if __name__ == "__main__":
    fetch()

