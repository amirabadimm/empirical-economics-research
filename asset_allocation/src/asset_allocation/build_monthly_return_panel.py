"""Build canonical Solar Hijri month-end levels and monthly asset returns."""

from __future__ import annotations

import csv
import os
import tempfile
import re
import zipfile
from collections import defaultdict
from datetime import date
from decimal import Decimal
from pathlib import Path
from xml.etree import ElementTree

import jdatetime


PROJECT_ROOT = Path(__file__).resolve().parents[2]
GOLD_PATH = PROJECT_ROOT / "data/raw/gold_18k/tgju_gold_18k_daily.csv"
EQUITY_PATH = PROJECT_ROOT / "data/raw/tse_total_index/tedpix_daily.csv"
FIXED_INCOME_PATH = PROJECT_ROOT / "data/raw/fixed_income/etf/etemad.csv"
HOUSING_PATH = PROJECT_ROOT / "data/interim/cbi_tehran_housing_monthly_1395_1403M05.xlsx"
KILID_PATH = PROJECT_ROOT / "data/raw/housing/kilid/snapshots/455cd4d7f670e77bd8a5928301d3e321b6e879157ac38b2beff9a4751755c807.html"
LEVELS_PATH = PROJECT_ROOT / "data/processed/analysis/monthly_asset_levels.csv"
RETURNS_PATH = PROJECT_ROOT / "data/processed/analysis/monthly_asset_returns.csv"
START_LEVEL_PERIOD = "1394/12"
START_RETURN_PERIOD = "1395/01"
END_PERIOD = "1405/05"
ASSETS = ("gold_18k", "equity_tedpix", "fixed_income_etemad", "tehran_housing")
RETURN_DEFINITIONS = {
    "gold_18k": "price_appreciation",
    "equity_tedpix": "total_return_index_level_change",
    "fixed_income_etemad": "market_price_return_no_periodic_distribution",
    "tehran_housing": "transaction_price_appreciation_excludes_rent",
}
UNITS = {
    "gold_18k": "IRR_per_gram",
    "equity_tedpix": "index_points",
    "fixed_income_etemad": "IRR_per_fund_unit",
    "tehran_housing": "million_IRR_per_m2",
}
SOURCE_FILES = {
    "gold_18k": "data/raw/gold_18k/tgju_gold_18k_daily.csv",
    "equity_tedpix": "data/raw/tse_total_index/tedpix_daily.csv",
    "fixed_income_etemad": "data/raw/fixed_income/etf/etemad.csv",
    "tehran_housing": "CBI_through_1403_05_then_chain_linked_Kilid",
}
LEVEL_FIELDS = (
    "jalali_period", "jalali_year", "jalali_month", "asset_id", "month_end_level",
    "raw_source_level", "link_factor", "unit",
    "source_observation_date", "source_method", "source_file", "return_definition",
    "data_quality_flag",
)
RETURN_FIELDS = (
    "jalali_period", "jalali_year", "jalali_month", "asset_id", "previous_jalali_period",
    "previous_month_end_level", "current_month_end_level", "monthly_return", "return_definition",
    "current_source_observation_date", "previous_source_observation_date", "source_file",
    "data_quality_flag", "missing_reason",
)


def periods(start: str, end: str) -> list[str]:
    start_year, start_month = map(int, start.split("/"))
    end_year, end_month = map(int, end.split("/"))
    result = []
    year, month = start_year, start_month
    while (year, month) <= (end_year, end_month):
        result.append(f"{year:04}/{month:02}")
        year, month = (year + 1, 1) if month == 12 else (year, month + 1)
    return result


def previous_period(period: str) -> str:
    year, month = map(int, period.split("/"))
    return f"{year - 1:04}/12" if month == 1 else f"{year:04}/{month - 1:02}"


def gregorian_to_period(value: str) -> str:
    converted = jdatetime.date.fromgregorian(date=date.fromisoformat(value))
    return f"{converted.year:04}/{converted.month:02}"


def read_daily_month_ends(
    path: Path, asset_id: str, level_field: str, *, require_trade: bool = False
) -> dict[str, dict[str, str]]:
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    seen_dates: set[str] = set()
    with path.open(encoding="utf-8-sig", newline="") as source:
        for row in csv.DictReader(source):
            source_date = row["source_date_gregorian"]
            if source_date in seen_dates:
                raise ValueError(f"Duplicate {asset_id} source date: {source_date}")
            seen_dates.add(source_date)
            if require_trade and row["has_trade"].lower() != "true":
                continue
            level = Decimal(row[level_field])
            if not level.is_finite() or level <= 0:
                raise ValueError(f"Invalid {asset_id} level on {source_date}: {level}")
            grouped[gregorian_to_period(source_date)].append(row)
    return {
        period: max(rows, key=lambda row: row["source_date_gregorian"])
        for period, rows in grouped.items()
    }


def _xlsx_rows(path: Path, sheet_name: str) -> list[dict[str, str]]:
    main_ns = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
    rel_ns = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
    pkg_rel_ns = "http://schemas.openxmlformats.org/package/2006/relationships"
    with zipfile.ZipFile(path) as archive:
        shared: list[str] = []
        if "xl/sharedStrings.xml" in archive.namelist():
            root = ElementTree.fromstring(archive.read("xl/sharedStrings.xml"))
            shared = ["".join(node.text or "" for node in item.iter(f"{{{main_ns}}}t"))
                      for item in root]
        workbook = ElementTree.fromstring(archive.read("xl/workbook.xml"))
        relationships = ElementTree.fromstring(archive.read("xl/_rels/workbook.xml.rels"))
        targets = {item.attrib["Id"]: item.attrib["Target"]
                   for item in relationships.findall(f"{{{pkg_rel_ns}}}Relationship")}
        sheet = next(item for item in workbook.iter(f"{{{main_ns}}}sheet")
                     if item.attrib["name"] == sheet_name)
        target = targets[sheet.attrib[f"{{{rel_ns}}}id"]].lstrip("/")
        member = target if target.startswith("xl/") else f"xl/{target}"
        root = ElementTree.fromstring(archive.read(member))
        matrix: list[list[str]] = []
        for row in root.iter(f"{{{main_ns}}}row"):
            values: dict[int, str] = {}
            for cell in row.findall(f"{{{main_ns}}}c"):
                reference = cell.attrib["r"]
                letters = "".join(char for char in reference if char.isalpha())
                column = 0
                for char in letters:
                    column = column * 26 + ord(char.upper()) - 64
                value_node = cell.find(f"{{{main_ns}}}v")
                value = "" if value_node is None else (value_node.text or "")
                if cell.attrib.get("t") == "s" and value:
                    value = shared[int(value)]
                elif cell.attrib.get("t") == "inlineStr":
                    value = "".join(node.text or "" for node in cell.iter(f"{{{main_ns}}}t"))
                values[column - 1] = value
            width = max(values, default=-1) + 1
            matrix.append([values.get(index, "") for index in range(width)])
    headers = matrix[0]
    return [dict(zip(headers, row + [""] * (len(headers) - len(row)))) for row in matrix[1:]]


def read_housing() -> dict[str, dict[str, str]]:
    rows = _xlsx_rows(HOUSING_PATH, "Monthly_Citywide")
    result: dict[str, dict[str, str]] = {}
    for row in rows:
        period = row["date_jalali"]
        if period in result:
            raise ValueError(f"Duplicate housing month: {period}")
        level = Decimal(row["avg_price_million_irr_per_m2"])
        if not level.is_finite() or level <= 0:
            raise ValueError(f"Invalid housing level in {period}: {level}")
        result[period] = row
    return result


def read_kilid() -> dict[str, dict[str, str]]:
    text = KILID_PATH.read_text(encoding="utf-8")
    pattern = re.compile(
        r'\\"children\\":\\"([^\\"]+ - 1[34]\d{2})\\".*?'
        r'\\"children\\":\\"([^\\"]+ میلیون تومان)\\"'
    )
    digit_map = str.maketrans("۰۱۲۳۴۵۶۷۸۹٫", "0123456789.")
    month_numbers = {
        "فروردین": 1, "اردیبهشت": 2, "خرداد": 3, "تیر": 4, "مرداد": 5,
        "شهریور": 6, "مهر": 7, "آبان": 8, "آذر": 9, "دی": 10,
        "بهمن": 11, "اسفند": 12,
    }
    result: dict[str, dict[str, str]] = {}
    for label, price_label in pattern.findall(text):
        month_name, year = (part.strip() for part in label.split("-"))
        period = f"{year}/{month_numbers[month_name]:02}"
        if period in result:
            raise ValueError(f"Duplicate Kilid housing month: {period}")
        price_million_toman = Decimal(price_label.split()[0].translate(digit_map))
        result[period] = {
            "date_jalali": period,
            "avg_price_million_irr_per_m2": str(price_million_toman * 10),
        }
    if not result:
        raise ValueError("Kilid snapshot contains no monthly Tehran observations")
    return result


def atomic_write(path: Path, fields: tuple[str, ...], rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8-sig", newline="", delete=False, dir=path.parent, suffix=".tmp"
    ) as file:
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
        temporary = Path(file.name)
    os.replace(temporary, path)


def build() -> dict[str, int | str]:
    gold = read_daily_month_ends(GOLD_PATH, "gold_18k", "price_close_irr_per_gram")
    equity = read_daily_month_ends(EQUITY_PATH, "equity_tedpix", "index_close")
    fixed_income = read_daily_month_ends(
        FIXED_INCOME_PATH, "fixed_income_etemad", "closing_price_irr", require_trade=True
    )
    cbi_housing = read_housing()
    kilid_housing = read_kilid()
    overlap = sorted(set(cbi_housing) & set(kilid_housing))
    if len(overlap) < 12 or "1403/05" not in overlap:
        raise ValueError("Insufficient CBI–Kilid overlap for an auditable boundary link")
    cbi_boundary = Decimal(cbi_housing["1403/05"]["avg_price_million_irr_per_m2"])
    kilid_boundary = Decimal(kilid_housing["1403/05"]["avg_price_million_irr_per_m2"])
    kilid_link_factor = cbi_boundary / kilid_boundary
    housing: dict[str, dict[str, str]] = {}
    for period, row in cbi_housing.items():
        housing[period] = {
            **row,
            "_raw_level": row["avg_price_million_irr_per_m2"],
            "_link_factor": "1",
            "_source_method": "CBI_reported_monthly_value",
            "_source_file": "data/interim/cbi_tehran_housing_monthly_1395_1403M05.xlsx",
            "_quality_flag": "ok",
        }
    for period, row in kilid_housing.items():
        if period <= "1403/05":
            continue
        raw_level = Decimal(row["avg_price_million_irr_per_m2"])
        housing[period] = {
            **row,
            "avg_price_million_irr_per_m2": format(
                (raw_level * kilid_link_factor).quantize(Decimal("0.000001")), "f"
            ),
            "_raw_level": format(raw_level, "f"),
            "_link_factor": format(kilid_link_factor, ".12f"),
            "_source_method": "Kilid_chain_linked_to_CBI_1403_05",
            "_source_file": "data/raw/housing/kilid/snapshots/455cd4d7f670e77bd8a5928301d3e321b6e879157ac38b2beff9a4751755c807.html",
            "_quality_flag": "secondary_proxy_low_overlap_similarity",
        }
    sources = {
        "gold_18k": (gold, "price_close_irr_per_gram", "last_valid_TGJU_observation"),
        "equity_tedpix": (equity, "index_close", "last_valid_TSETMC_observation"),
        "fixed_income_etemad": (
            fixed_income, "closing_price_irr", "last_traded_TSETMC_observation"
        ),
        "tehran_housing": (housing, "avg_price_million_irr_per_m2", "housing_source_specific_monthly_value"),
    }
    levels: list[dict[str, str]] = []
    level_lookup: dict[tuple[str, str], dict[str, str]] = {}
    for period in periods(START_LEVEL_PERIOD, END_PERIOD):
        year, month = period.split("/")
        for asset_id in ASSETS:
            rows, field, method = sources[asset_id]
            row = rows.get(period)
            source_date = ""
            level = ""
            raw_level = ""
            link_factor = ""
            flag = "missing_source_observation"
            source_file = SOURCE_FILES[asset_id]
            if row is not None:
                level = row[field]
                raw_level = row.get("_raw_level", level)
                link_factor = row.get("_link_factor", "1")
                source_date = (row.get("source_date_jalali") or row.get("source_date_gregorian")
                               or row.get("date_jalali") or "")
                if asset_id == "fixed_income_etemad":
                    flag = "provisional_distribution_policy_audit"
                else:
                    flag = row.get("_quality_flag", "ok")
                method = row.get("_source_method", method)
                source_file = row.get("_source_file", source_file)
            record = {
                "jalali_period": period,
                "jalali_year": year,
                "jalali_month": month,
                "asset_id": asset_id,
                "month_end_level": level,
                "raw_source_level": raw_level,
                "link_factor": link_factor,
                "unit": UNITS[asset_id],
                "source_observation_date": source_date,
                "source_method": method,
                "source_file": source_file,
                "return_definition": RETURN_DEFINITIONS[asset_id],
                "data_quality_flag": flag,
            }
            levels.append(record)
            level_lookup[(period, asset_id)] = record

    returns: list[dict[str, str]] = []
    for period in periods(START_RETURN_PERIOD, END_PERIOD):
        year, month = period.split("/")
        prior = previous_period(period)
        for asset_id in ASSETS:
            current = level_lookup[(period, asset_id)]
            previous = level_lookup[(prior, asset_id)]
            monthly_return = ""
            missing_reason = ""
            flag = current["data_quality_flag"]
            if not current["month_end_level"]:
                missing_reason = "missing_current_month_level"
                flag = "missing_return"
            elif not previous["month_end_level"]:
                missing_reason = "missing_previous_month_level"
                flag = "missing_return"
            else:
                value = Decimal(current["month_end_level"]) / Decimal(previous["month_end_level"]) - 1
                monthly_return = format(value.quantize(Decimal("0.000000000001")), "f")
            returns.append({
                "jalali_period": period,
                "jalali_year": year,
                "jalali_month": month,
                "asset_id": asset_id,
                "previous_jalali_period": prior,
                "previous_month_end_level": previous["month_end_level"],
                "current_month_end_level": current["month_end_level"],
                "monthly_return": monthly_return,
                "return_definition": RETURN_DEFINITIONS[asset_id],
                "current_source_observation_date": current["source_observation_date"],
                "previous_source_observation_date": previous["source_observation_date"],
                "source_file": current["source_file"],
                "data_quality_flag": flag,
                "missing_reason": missing_reason,
            })

    atomic_write(LEVELS_PATH, LEVEL_FIELDS, levels)
    atomic_write(RETURNS_PATH, RETURN_FIELDS, returns)
    return {
        "level_rows": len(levels),
        "return_rows": len(returns),
        "level_periods": len(periods(START_LEVEL_PERIOD, END_PERIOD)),
        "return_periods": len(periods(START_RETURN_PERIOD, END_PERIOD)),
        "levels_output": str(LEVELS_PATH),
        "returns_output": str(RETURNS_PATH),
    }


if __name__ == "__main__":
    print(build())
