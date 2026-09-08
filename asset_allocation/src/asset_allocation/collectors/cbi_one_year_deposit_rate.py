"""Materialize the user-supplied CBI annual one-year deposit-rate table."""

from __future__ import annotations

import csv
import os
import tempfile
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
RAW_DIR = PROJECT_ROOT / "data" / "raw" / "fixed_income" / "bank_deposits"
CSV_PATH = RAW_DIR / "cbi_one_year_deposit_rate_annual.csv"
SOURCE_URL = "https://cbi.ir/simplelist/1515.aspx"
CSV_FIELDS = (
    "jalali_year", "one_year_rate_text_percent", "selected_one_year_rate_percent",
    "selection_rule", "source_name", "source_url", "extraction_basis",
)

# Direct transcription of the CBI table supplied by the user. Intervals use their upper endpoint.
OBSERVATIONS = (
    ("1384", "13", "13", "single value"),
    ("1385", "7-16", "16", "upper endpoint of CBI interval"),
    ("1386", "7-16", "16", "upper endpoint of CBI interval"),
    ("1387", "maximum 15", "15", "CBI maximum"),
    ("1388", "14.5", "14.5", "single value"),
    ("1389", "14", "14", "single value"),
    ("1390", "6-20", "20", "upper endpoint of CBI interval"),
    ("1391", "7-20", "20", "upper endpoint of CBI interval"),
    ("1392", "7-20", "20", "upper endpoint of CBI interval"),
    ("1393", "22", "22", "single value"),
    ("1394", "20", "20", "single value"),
    ("1395", "18", "18", "single value"),
    ("1396", "15", "15", "single value"),
)


def collect() -> dict[str, str | int]:
    records = [
        {
            "jalali_year": year,
            "one_year_rate_text_percent": original,
            "selected_one_year_rate_percent": selected,
            "selection_rule": rule,
            "source_name": "Central Bank of Iran annual term-deposit interest-rate table",
            "source_url": SOURCE_URL,
            "extraction_basis": "Manual transcription from official CBI table supplied by user; CBI site blocks automated retrieval.",
        }
        for year, original, selected, rule in OBSERVATIONS
    ]
    write_canonical_csv(records)
    return {"records": len(records), "first_year": OBSERVATIONS[0][0], "last_year": OBSERVATIONS[-1][0], "csv": str(CSV_PATH)}


def write_canonical_csv(records: list[dict[str, str]]) -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", delete=False, dir=RAW_DIR, suffix=".tmp") as file:
        writer = csv.DictWriter(file, fieldnames=CSV_FIELDS)
        writer.writeheader()
        writer.writerows(records)
        temporary = Path(file.name)
    os.replace(temporary, CSV_PATH)


if __name__ == "__main__":
    print(collect())
