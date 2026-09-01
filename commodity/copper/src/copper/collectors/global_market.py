"""Collect public first-wave global copper-market datasets.

The collector archives every response immutably and writes one canonical CSV per
source family atomically. Existing LME data are intentionally out of scope.
"""

from __future__ import annotations

import argparse
import csv
import io
import json
import time
import urllib.error
import urllib.parse
import urllib.request
import zipfile
from datetime import datetime, timezone
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parents[3]
RAW_DIR = PROJECT_DIR / "data" / "raw" / "global_market"
USER_AGENT = "empirical-economics-research copper collector/1.0"

FRED_SERIES = {
    "DTWEXBGS": ("broad_us_dollar_index", "index_2006_01_100"),
    "EFFR": ("effective_federal_funds_rate", "percent_per_year"),
    "DGS10": ("us_10y_treasury_yield", "percent_per_year"),
    "DFII10": ("us_10y_real_treasury_yield", "percent_per_year"),
    "DEXCHUS": ("cny_per_usd", "cny_per_usd"),
    "WPU10230101": ("us_no1_copper_scrap_ppi", "index_dec_1986_100"),
    "WPU10230102": ("us_no2_copper_scrap_ppi", "index_dec_1986_100"),
}

NBS_SERIES = {
    "A02091J01": "copper_products_output_current_period",
    "A02091J02": "copper_products_output_accumulated",
    "A02091J03": "copper_products_output_yoy",
    "A02091J04": "copper_products_output_accumulated_yoy",
}

IRENA_URL = (
    "https://pxweb.irena.org/api/v1/en/IRENASTAT/Power%20Capacity%20and%20Generation/"
    "Region_ELECCAP_2026_H1_v-PX%201.px"
)


def _timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _request(url: str, timeout: int, data: bytes | None = None, retries: int = 5) -> bytes:
    last_error: Exception | None = None
    for attempt in range(retries):
        request = urllib.request.Request(
            url,
            data=data,
            headers={"User-Agent": USER_AGENT, "Content-Type": "application/json"},
        )
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                return response.read()
        except (OSError, urllib.error.HTTPError, urllib.error.URLError) as error:
            last_error = error
            if isinstance(error, urllib.error.HTTPError) and error.code < 500 and error.code != 429:
                raise
            if attempt + 1 < retries:
                time.sleep(2 ** attempt)
    raise RuntimeError(f"Request failed after {retries} attempts: {url}") from last_error


def _archive(source: str, suffix: str, payload: bytes) -> Path:
    directory = RAW_DIR / source / "snapshots"
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / f"{source}_{_timestamp()}.{suffix}"
    counter = 1
    while path.exists():
        path = directory / f"{source}_{_timestamp()}_{counter}.{suffix}"
        counter += 1
    with path.open("xb") as handle:
        handle.write(payload)
    return path


def _write_csv(source: str, filename: str, fields: list[str], rows: list[dict]) -> Path:
    directory = RAW_DIR / source
    directory.mkdir(parents=True, exist_ok=True)
    output = directory / filename
    temporary = output.with_suffix(output.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    temporary.replace(output)
    return output


def collect_fred(timeout: int) -> tuple[Path, int]:
    rows: list[dict] = []
    fetched_at = datetime.now(timezone.utc).isoformat()
    for series_id, (indicator, unit) in FRED_SERIES.items():
        url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={series_id}"
        payload = _request(url, timeout)
        _archive("fred", "csv", payload)
        for row in csv.DictReader(io.StringIO(payload.decode("utf-8-sig"))):
            value = row.get(series_id, ".")
            if value in {None, "", "."}:
                continue
            rows.append({
                "date": row["observation_date"], "series_id": series_id,
                "indicator": indicator, "value": value, "unit": unit,
                "source_url": url, "fetched_at_utc": fetched_at,
            })
    rows.sort(key=lambda row: (row["series_id"], row["date"]))
    fields = ["date", "series_id", "indicator", "value", "unit", "source_url", "fetched_at_utc"]
    return _write_csv("fred", "fred_copper_controls_raw.csv", fields, rows), len(rows)


def collect_nbs(timeout: int) -> tuple[Path, int]:
    rows: list[dict] = []
    fetched_at = datetime.now(timezone.utc).isoformat()
    for code, indicator in NBS_SERIES.items():
        url = f"https://api.db.nomics.world/v22/series/NBS/M_A02091J/{code}?observations=1"
        payload = _request(url, timeout)
        _archive("nbs_dbnomics", "json", payload)
        document = json.loads(payload)["series"]["docs"][0]
        for period, value in zip(document["period"], document["value"]):
            if value in {None, "NA"}:
                continue
            rows.append({
                "period": period, "series_code": code, "indicator": indicator,
                "value": value,
                "unit": "10_thousand_metric_tonnes" if code in {"A02091J01", "A02091J02"} else "percent",
                "dataset": document.get("dataset_name", "Copper Products"),
                "source_url": url, "fetched_at_utc": fetched_at,
            })
    rows.sort(key=lambda row: (row["series_code"], row["period"]))
    fields = ["period", "series_code", "indicator", "value", "unit", "dataset", "source_url", "fetched_at_utc"]
    return _write_csv("nbs_dbnomics", "china_copper_products_raw.csv", fields, rows), len(rows)


def collect_irena(timeout: int) -> tuple[Path, int]:
    query = {
        "query": [
            {"code": "Region", "selection": {"filter": "item", "values": ["GLO"]}},
            {"code": "Technology", "selection": {"filter": "all", "values": ["*"]}},
            {"code": "Grid connection", "selection": {"filter": "all", "values": ["*"]}},
            {"code": "Year", "selection": {"filter": "all", "values": ["*"]}},
        ],
        "response": {"format": "json-stat2"},
    }
    payload = _request(IRENA_URL, timeout, json.dumps(query).encode())
    _archive("irena", "json", payload)
    data = json.loads(payload)
    dimensions = data["id"]
    sizes = data["size"]
    labels: list[list[str]] = []
    for dimension in dimensions:
        category = data["dimension"][dimension]["category"]
        ordered = sorted(category["index"], key=category["index"].get)
        labels.append([category.get("label", {}).get(item, item) for item in ordered])
    rows: list[dict] = []
    fetched_at = datetime.now(timezone.utc).isoformat()
    for flat_index, value in enumerate(data["value"]):
        if value is None:
            continue
        remainder = flat_index
        coords = [0] * len(sizes)
        for index in range(len(sizes) - 1, -1, -1):
            coords[index] = remainder % sizes[index]
            remainder //= sizes[index]
        row = {dimensions[i]: labels[i][coords[i]] for i in range(len(dimensions))}
        row.update({"capacity_mw": value, "source_url": IRENA_URL, "fetched_at_utc": fetched_at})
        rows.append(row)
    fields = dimensions + ["capacity_mw", "source_url", "fetched_at_utc"]
    return _write_csv("irena", "world_power_capacity_raw.csv", fields, rows), len(rows)


def collect_bgs(timeout: int) -> tuple[Path, int]:
    base = "https://ogcapi.bgs.ac.uk/collections/world-mineral-statistics/items"
    params = {"f": "json", "limit": "1000", "filter-lang": "cql-text", "filter": "erml_group='Copper'"}
    features: list[dict] = []
    offset = 0
    number_matched: int | None = None
    while number_matched is None or offset < number_matched:
        page_params = params | {"offset": str(offset)}
        url = base + "?" + urllib.parse.urlencode(page_params)
        payload = _request(url, timeout)
        _archive("bgs", "json", payload)
        page = json.loads(payload)
        page_features = page.get("features", [])
        if not page_features:
            break
        features.extend(page_features)
        number_matched = int(page.get("numberMatched", len(features)))
        offset += len(page_features)
        time.sleep(0.2)
    rows = [feature["properties"] for feature in features]
    if not rows:
        raise RuntimeError("BGS returned no copper rows; canonical output was not replaced")
    fields = sorted({key for row in rows for key in row})
    rows.sort(key=lambda row: (str(row.get("erml_commodity")), str(row.get("country_iso3_code")), str(row.get("year"))))
    return _write_csv("bgs", "world_copper_statistics_raw.csv", fields, rows), len(rows)


def collect_cftc(timeout: int, start_year: int) -> tuple[Path, int]:
    rows: list[dict] = []
    current_year = datetime.now(timezone.utc).year
    for year in range(start_year, current_year + 1):
        url = f"https://www.cftc.gov/files/dea/history/fut_disagg_txt_{year}.zip"
        try:
            payload = _request(url, timeout)
        except urllib.error.HTTPError as error:
            if error.code == 404 and year == current_year:
                continue
            raise
        _archive("cftc", "zip", payload)
        with zipfile.ZipFile(io.BytesIO(payload)) as archive:
            names = [name for name in archive.namelist() if name.lower().endswith(".txt")]
            if len(names) != 1:
                raise RuntimeError(f"Unexpected CFTC archive layout for {year}: {names}")
            text = archive.read(names[0]).decode("utf-8-sig", errors="replace")
        for row in csv.DictReader(io.StringIO(text)):
            market = row.get("Market_and_Exchange_Names", "")
            contract_code = row.get("CFTC_Contract_Market_Code", "").strip().lstrip("0")
            if (
                "COMMODITY EXCHANGE" in market.upper()
                and contract_code == "85692"
            ):
                row["source_year"] = year
                row["source_url"] = url
                rows.append(row)
        time.sleep(0.1)
    if not rows:
        raise RuntimeError("CFTC archives contained no COMEX copper rows")
    fields = list(rows[0])
    return _write_csv("cftc", "comex_copper_disaggregated_cot_raw.csv", fields, rows), len(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sources", nargs="+", default=["fred", "nbs", "irena", "bgs", "cftc"])
    parser.add_argument("--timeout", type=int, default=120)
    parser.add_argument("--cftc-start-year", type=int, default=2006)
    args = parser.parse_args()
    collectors = {
        "fred": lambda: collect_fred(args.timeout),
        "nbs": lambda: collect_nbs(args.timeout),
        "irena": lambda: collect_irena(args.timeout),
        "bgs": lambda: collect_bgs(args.timeout),
        "cftc": lambda: collect_cftc(args.timeout, args.cftc_start_year),
    }
    for source in args.sources:
        if source not in collectors:
            raise SystemExit(f"Unknown source: {source}")
        path, count = collectors[source]()
        print(f"{source}: {count:,} rows -> {path}")


if __name__ == "__main__":
    main()
