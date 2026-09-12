"""Audit the extracted CBI Tehran monthly housing workbook without modifying it."""

import math
import statistics
import zipfile
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
HOUSING_PATH = PROJECT_ROOT / "data/interim/cbi_tehran_housing_monthly_1395_1403M05.xlsx"
AUDIT_OUTPUT_PATH = PROJECT_ROOT / "data/processed/analysis/housing_data_quality_audit.csv"
AUDIT_FIELDS = (
    "jalali_period",
    "year",
    "month",
    "price_level",
    "normalized_unit",
    "original_extracted_level",
    "source_pdf",
    "provenance_method",
    "quality_flag",
    "verification_source",
    "verification_evidence",
    "previous_period",
    "monthly_return",
    "diagnostic_flag",
    "audit_note",
)


def period_shift(period: str, months: int) -> str:
    year, month = map(int, period.split("/"))
    serial = year * 12 + month - 1 + months
    return f"{serial // 12:04d}/{serial % 12 + 1:02d}"


def _column_index(ref: str) -> int:
    letters = "".join(c for c in ref if c.isalpha())
    result = 0
    for char in letters:
        result = result * 26 + ord(char.upper()) - 64
    return result - 1


def read_xlsx_sheets(path: Path) -> dict[str, list[dict[str, str | None]]]:
    """Read the simple value-only audit workbook with Python's standard library."""
    ns = {
        "m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
        "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
    }
    sheets: dict[str, list[dict[str, str | None]]] = {}
    with zipfile.ZipFile(path) as archive:
        workbook = ET.fromstring(archive.read("xl/workbook.xml"))
        relationships = ET.fromstring(archive.read("xl/_rels/workbook.xml.rels"))
        relmap = {item.attrib["Id"]: item.attrib["Target"] for item in relationships}
        for sheet in workbook.find("m:sheets", ns):
            name = sheet.attrib["name"]
            target = relmap[sheet.attrib[f"{{{ns['r']}}}id"]].lstrip("/")
            if not target.startswith("xl/"):
                target = "xl/" + target
            root = ET.fromstring(archive.read(target))
            matrix: list[list[str | None]] = []
            for row in root.findall(".//m:sheetData/m:row", ns):
                values: dict[int, str | None] = {}
                for cell in row.findall("m:c", ns):
                    value = cell.find("m:v", ns)
                    values[_column_index(cell.attrib["r"])] = None if value is None else value.text
                matrix.append([values.get(i) for i in range(max(values, default=-1) + 1)])
            headers = matrix[0]
            sheets[name] = [dict(zip(headers, row)) for row in matrix[1:]]
    return sheets


def audit_workbook(path: Path = HOUSING_PATH) -> dict[str, object]:
    sheets = read_xlsx_sheets(path)
    monthly = sheets["Monthly_Citywide"]
    reports = {row["report_period"]: row for row in sheets["Report_Audit"]}
    periods = [row["date_jalali"] for row in monthly]
    prices = {row["date_jalali"]: float(row["avg_price_million_irr_per_m2"]) for row in monthly}

    expected = []
    period = min(prices)
    while period <= max(prices):
        expected.append(period)
        period = period_shift(period, 1)

    large_moves = []
    order_flags = []
    mismatches = []
    for period in sorted(prices):
        previous = period_shift(period, -1)
        if previous in prices:
            monthly_return = prices[period] / prices[previous] - 1
            if abs(monthly_return) > 0.25:
                large_moves.append((period, prices[previous], prices[period], monthly_return))
        neighbors = [prices[p] for p in (previous, period_shift(period, 1)) if p in prices]
        if neighbors and (prices[period] < min(neighbors) / 5 or prices[period] > max(neighbors) * 5):
            order_flags.append((period, prices[period], neighbors))

        evidence = []
        if period in reports and reports[period].get("table2_current_month_price_million_irr_m2"):
            evidence.append(("current_report", period, float(reports[period]["table2_current_month_price_million_irr_m2"])))
        next_period = period_shift(period, 1)
        if next_period in reports and reports[next_period].get("table2_previous_month_price_million_irr_m2"):
            evidence.append(("next_report_previous", next_period, float(reports[next_period]["table2_previous_month_price_million_irr_m2"])))
        next_year = period_shift(period, 12)
        if next_year in reports and reports[next_year].get("table2_same_month_prev_year_price_million_irr_m2"):
            evidence.append(("next_year_same_month", next_year, float(reports[next_year]["table2_same_month_prev_year_price_million_irr_m2"])))
        if evidence and any(abs(value - prices[period]) > 0.001 for _, _, value in evidence):
            mismatches.append((period, prices[period], evidence))

    return {
        "row_count": len(monthly),
        "duplicate_periods": sorted(period for period, count in Counter(periods).items() if count > 1),
        "missing_periods": sorted(set(expected) - set(prices)),
        "nonpositive_levels": sorted((period, value) for period, value in prices.items() if not math.isfinite(value) or value <= 0),
        "large_moves": large_moves,
        "order_of_magnitude_flags": order_flags,
        "official_evidence_mismatches": mismatches,
    }


def build_audit_report() -> dict[str, object]:
    """Write one auditable row per corrected CBI month with non-destructive diagnostics."""
    from asset_allocation.build_monthly_return_panel import atomic_write, read_housing

    housing = read_housing()
    rows = []
    extreme_periods = []
    for period in sorted(housing):
        row = housing[period]
        year, month = period.split("/")
        previous = period_shift(period, -1)
        monthly_return = ""
        diagnostic = ""
        if previous in housing:
            value = float(row["avg_price_million_irr_per_m2"]) / float(
                housing[previous]["avg_price_million_irr_per_m2"]
            ) - 1
            monthly_return = f"{value:.12f}"
            if abs(value) > 0.25:
                diagnostic = "large_monthly_change_review"
                extreme_periods.append(period)
        rows.append(
            {
                "jalali_period": period,
                "year": year,
                "month": month,
                "price_level": row["avg_price_million_irr_per_m2"],
                "normalized_unit": "million_IRR_per_m2",
                "original_extracted_level": row.get(
                    "_raw_level", row["avg_price_million_irr_per_m2"]
                ),
                "source_pdf": row.get(
                    "_source_report", f"data/raw/housing/cbi/reports/{row['source_pdf']}"
                ),
                "provenance_method": row["provenance_method"],
                "quality_flag": row.get("_quality_flag", "ok"),
                "verification_source": row.get("_verification_source", ""),
                "verification_evidence": row.get("_verification_evidence", ""),
                "previous_period": previous if previous in housing else "",
                "monthly_return": monthly_return,
                "diagnostic_flag": diagnostic,
                "audit_note": row.get("_audit_note", ""),
            }
        )
    atomic_write(AUDIT_OUTPUT_PATH, AUDIT_FIELDS, rows)
    return {
        "row_count": len(rows),
        "extreme_return_periods": extreme_periods,
        "output": str(AUDIT_OUTPUT_PATH),
    }


def annual_statistics(levels: dict[str, float], year: int) -> dict[str, object]:
    periods = [f"{year}/{month:02d}" for month in range(1, 13)]
    returns = []
    for period in periods:
        previous = f"{year - 1}/12" if period.endswith("/01") else period_shift(period, -1)
        returns.append(levels[period] / levels[previous] - 1)
    monthly_standard_deviation = statistics.stdev(returns)
    return {
        "monthly_returns": dict(zip(periods, returns)),
        "compounded_return": math.prod(1 + value for value in returns) - 1,
        "monthly_standard_deviation": monthly_standard_deviation,
        "annualized_volatility": monthly_standard_deviation * math.sqrt(12),
    }


def comparison_1397() -> dict[str, dict[str, object]]:
    """Isolate the Mehr text-layer error from all verified source adjudications."""
    from asset_allocation.build_monthly_return_panel import read_housing

    raw_rows = read_xlsx_sheets(HOUSING_PATH)["Monthly_Citywide"]
    raw = {
        row["date_jalali"]: float(row["avg_price_million_irr_per_m2"])
        for row in raw_rows
    }
    only_mehr_fixed = dict(raw)
    only_mehr_fixed["1397/07"] = 86.109
    corrected = {
        period: float(row["avg_price_million_irr_per_m2"])
        for period, row in read_housing().items()
    }
    return {
        "before": annual_statistics(raw, 1397),
        "only_1397_07_corrected": annual_statistics(only_mehr_fixed, 1397),
        "after_all_verified_corrections": annual_statistics(corrected, 1397),
    }


if __name__ == "__main__":
    for key, value in audit_workbook().items():
        print(f"{key}: {value}")
    print(f"corrected_audit_report: {build_audit_report()}")
    print(f"comparison_1397: {comparison_1397()}")
