"""Collect COCHILCO Chilean mine production by company from its electronic bulletin."""

from __future__ import annotations

import argparse
import csv
import io
import re
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import requests
import truststore


PROJECT_DIR = Path(__file__).resolve().parents[3]
SOURCE_DIR = PROJECT_DIR / "data" / "raw" / "global_market" / "cochilco"
URL = "https://boletin.cochilco.cl/productos/boletin.asp"
NUMBER = re.compile(r"^(?:-|\d{1,3}(?:\.\d{3})*,\d+|\d+,\d+)$")
FIELDS = [
    "period", "frequency", "parent_company", "company", "value_kmt_copper_content",
    "provisional", "source_report_year", "source_report_month", "source_url",
    "fetched_at_utc",
]


def parse_vector(value: object) -> list[float | None]:
    tokens = [token for token in str(value).split() if NUMBER.fullmatch(token)]
    result: list[float | None] = []
    for token in tokens:
        if token == "-":
            result.append(None)
        else:
            result.append(float(token.replace(".", "").replace(",", ".")))
    return result


def company_labels(table: pd.DataFrame) -> list[tuple[str, str]]:
    labels: list[tuple[str, str]] = []
    for column in range(1, table.shape[1]):
        parent = "" if pd.isna(table.iloc[0, column]) else str(table.iloc[0, column]).strip()
        child = "" if pd.isna(table.iloc[1, column]) else str(table.iloc[1, column]).strip()
        company = child if parent == "CODELCO" and child else parent or child
        labels.append((parent, company))
    return labels


def normalize(payload: bytes, report_year: int, report_month: int, source_url: str) -> list[dict]:
    tables = pd.read_html(io.BytesIO(payload), encoding="latin1")
    candidates = [table for table in tables if table.shape[1] >= 20 and table.shape[0] >= 10]
    if len(candidates) != 1:
        raise RuntimeError(f"Expected one COCHILCO production table, found {len(candidates)}")
    table = candidates[0]
    labels = company_labels(table)
    fetched_at = datetime.now(timezone.utc).isoformat()
    rows: list[dict] = []
    for row_index in range(2, table.shape[0]):
        label = str(table.iloc[row_index, 0])
        years = [int(year) for year in re.findall(r"\b(?:19|20)\d{2}\b", label)]
        if not years:
            continue
        is_monthly = "ENE/JAN" in label
        is_annual = bool(re.fullmatch(r"\s*(?:(?:19|20)\d{2}\s*)+", label))
        if not is_monthly and not is_annual:
            continue
        if is_monthly:
            years = years[:1]
        for column, (parent, company) in enumerate(labels, start=1):
            values = parse_vector(table.iloc[row_index, column])
            if not values:
                continue
            if is_monthly:
                if len(values) > 12:
                    raise RuntimeError(f"Too many monthly values for {company} {years[0]}")
                periods = [f"{years[0]:04d}-{month:02d}" for month in range(1, len(values) + 1)]
                frequency = "monthly"
            else:
                if len(values) != len(years):
                    continue
                periods = [str(year) for year in years]
                frequency = "annual"
            for period, value in zip(periods, values):
                rows.append({
                    "period": period,
                    "frequency": frequency,
                    "parent_company": parent,
                    "company": company,
                    "value_kmt_copper_content": value,
                    "provisional": str(years[0] == report_year and is_monthly).lower(),
                    "source_report_year": report_year,
                    "source_report_month": report_month,
                    "source_url": source_url,
                    "fetched_at_utc": fetched_at,
                })
    keys = [(row["period"], row["frequency"], row["parent_company"], row["company"]) for row in rows]
    if len(keys) != len(set(keys)):
        raise RuntimeError("Duplicate COCHILCO period/frequency/company keys")
    return rows


def fetch_report(report_year: int, report_month: int, timeout: int) -> list[dict]:
    truststore.inject_into_ssl()
    params = {"anio": str(report_year), "mes": f"{report_month:02d}", "tabla": "tabla22"}
    response = requests.get(URL, params=params, timeout=timeout, headers={"User-Agent": "Mozilla/5.0"})
    response.raise_for_status()
    snapshots = SOURCE_DIR / "snapshots"
    snapshots.mkdir(exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    with (snapshots / f"cochilco_company_production_{report_year}_{report_month:02d}_{stamp}.html").open("xb") as handle:
        handle.write(response.content)
    return normalize(response.content, report_year, report_month, response.url)


def collect(report_year: int, report_month: int, timeout: int, backfill: bool) -> tuple[Path, int]:
    SOURCE_DIR.mkdir(parents=True, exist_ok=True)
    reports = [(year, 1) for year in (2010, 2014, 2018, 2022, 2026)] if backfill else []
    if (report_year, report_month) not in reports:
        reports.append((report_year, report_month))
    combined: dict[tuple[str, str, str, str], dict] = {}
    for year, month in reports:
        for row in fetch_report(year, month, timeout):
            key = (row["period"], row["frequency"], row["parent_company"], row["company"])
            previous = combined.get(key)
            vintage = (row["source_report_year"], row["source_report_month"])
            previous_vintage = (
                (previous["source_report_year"], previous["source_report_month"])
                if previous else (-1, -1)
            )
            if vintage >= previous_vintage:
                combined[key] = row
    rows = sorted(
        combined.values(),
        key=lambda row: (row["frequency"], row["period"], row["parent_company"], row["company"]),
    )
    output = SOURCE_DIR / "chile_copper_mine_production_by_company_raw.csv"
    temporary = output.with_suffix(".csv.tmp")
    with temporary.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    temporary.replace(output)
    return output, len(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report-year", type=int, default=datetime.now().year)
    parser.add_argument("--report-month", type=int, default=datetime.now().month)
    parser.add_argument("--timeout", type=int, default=120)
    parser.add_argument("--backfill", action="store_true")
    args = parser.parse_args()
    path, count = collect(args.report_year, args.report_month, args.timeout, args.backfill)
    print(f"cochilco: {count:,} rows -> {path}")


if __name__ == "__main__":
    main()
