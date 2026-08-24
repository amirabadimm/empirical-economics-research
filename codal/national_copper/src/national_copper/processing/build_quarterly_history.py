"""Build standalone quarterly flows from Codal cumulative financial statements."""

from __future__ import annotations

import csv
import hashlib
import sys
from pathlib import Path

WORKSPACE_ROOT = Path(__file__).resolve().parents[5]
if str(WORKSPACE_ROOT) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_ROOT))

from codal.national_copper.src.national_copper.processing.statement_parsing import (
    PROJECT_ROOT,
    atomic_csv,
    parse_html,
    parse_xls,
)


INDEX_PATH = PROJECT_ROOT / "data" / "raw" / "financial_statements" / "filing_index.csv"
LEGACY_INDEX_PATH = PROJECT_ROOT / "data" / "raw" / "financial_statements" / "legacy_filing_index.csv"
OUTPUT_PATH = PROJECT_ROOT / "data" / "processed" / "national_copper_quarterly_financials.csv"
AVAILABILITY_PATH = PROJECT_ROOT / "data" / "processed" / "quarterly_availability.csv"

METRICS = (
    "operating_revenue_million_irr",
    "gross_profit_million_irr",
    "net_profit_million_irr",
    "direct_labor_cost_million_irr",
    "overhead_wages_million_irr",
    "sga_wages_million_irr",
    "other_overhead_expense_million_irr",
    "other_sga_expense_million_irr",
)


def source_audit(months: int) -> str:
    return "حسابرسی شده" if months == 12 else "حسابرسی نشده"


def parse_source(source: dict[str, str], required_audit: str) -> dict[str, int | None]:
    snapshot = PROJECT_ROOT / source["snapshot_path"]
    if hashlib.sha256(snapshot.read_bytes()).hexdigest() != source["snapshot_sha256"]:
        raise RuntimeError(f"Snapshot hash mismatch for {snapshot.name}")
    parser = parse_html if snapshot.suffix == ".html" else parse_xls
    return parser(snapshot, source["period_end_jalali"], required_audit)


def select_cumulative_sources() -> dict[tuple[str, int], dict[str, object]]:
    with INDEX_PATH.open(encoding="utf-8-sig", newline="") as stream:
        index = list(csv.DictReader(stream))
    grouped: dict[tuple[str, int], list[dict[str, str]]] = {}
    for source in index:
        year = source["period_end_jalali"][:4]
        months = int(source["statement_months"])
        if year < "1386" or year > "1405":
            continue
        grouped.setdefault((year, months), []).append(source)

    selected: dict[tuple[str, int], dict[str, object]] = {}
    for key, candidates in grouped.items():
        required_audit = source_audit(key[1])
        failures: list[str] = []
        for source in sorted(candidates, key=lambda row: row["publish_datetime_jalali"], reverse=True):
            try:
                metrics = parse_source(source, required_audit)
            except Exception as error:
                failures.append(f"{source['tracing_no']}: {error}")
                continue
            selected[key] = {"source": source, "metrics": metrics, "audit": required_audit}
            break
        if key not in selected:
            raise RuntimeError(f"No valid {required_audit} source for {key}: {'; '.join(failures)}")

    if LEGACY_INDEX_PATH.exists():
        with LEGACY_INDEX_PATH.open(encoding="utf-8-sig", newline="") as stream:
            for source in csv.DictReader(stream):
                snapshot = PROJECT_ROOT / source["snapshot_path"]
                if hashlib.sha256(snapshot.read_bytes()).hexdigest() != source["snapshot_sha256"]:
                    raise RuntimeError(f"Legacy snapshot hash mismatch for {snapshot.name}")
                if source["audit_status"] != source_audit(int(source["statement_months"])):
                    raise RuntimeError(f"Invalid legacy audit status for {source['period_end_jalali']}")
                metrics = {metric: None for metric in METRICS}
                for metric in METRICS[:3]:
                    metrics[metric] = int(source[metric])
                key = (source["period_end_jalali"][:4], int(source["statement_months"]))
                selected[key] = {"source": source, "metrics": metrics, "audit": source["audit_status"]}
    return selected


def difference(current: object, previous: object | None) -> int | None:
    if current is None or previous is None:
        return None
    return int(current) - int(previous)


def build() -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    cumulative = select_cumulative_sources()
    output: list[dict[str, object]] = []
    availability: list[dict[str, object]] = []

    for year in range(1386, 1406):
        year_text = str(year)
        for quarter, months, previous_months in ((1, 3, None), (2, 6, 3), (3, 9, 6), (4, 12, 9)):
            current = cumulative.get((year_text, months))
            previous = cumulative.get((year_text, previous_months)) if previous_months else None
            missing: list[str] = []
            if current is None:
                missing.append(f"{months}-month statement")
            if previous_months and previous is None:
                missing.append(f"{previous_months}-month statement")
            if missing:
                availability.append(
                    {
                        "fiscal_year_jalali": year_text,
                        "quarter": quarter,
                        "available": False,
                        "reason": "missing " + " and ".join(missing),
                    }
                )
                continue

            current_metrics = current["metrics"]
            previous_metrics = previous["metrics"] if previous else {metric: 0 for metric in METRICS}
            values = {
                metric: difference(current_metrics[metric], previous_metrics[metric])
                for metric in METRICS
            }
            wage_detail_available = all(values[metric] is not None for metric in METRICS[3:])
            current_source = current["source"]
            previous_source = previous["source"] if previous else None
            audit_basis = (
                "unaudited cumulative statement"
                if quarter == 1
                else "difference of two unaudited cumulative statements"
                if quarter in {2, 3}
                else "audited annual statement minus unaudited nine-month statement"
            )
            output.append(
                {
                    "fiscal_year_jalali": year_text,
                    "quarter": quarter,
                    "quarter_end_jalali": current_source["period_end_jalali"],
                    **values,
                    "wage_detail_available": wage_detail_available,
                    "labor_data_status": (
                        "provisional_pending_header_mapping_and_reconciliation"
                        if wage_detail_available
                        else "not_disclosed"
                    ),
                    "audit_basis": audit_basis,
                    "current_statement_months": months,
                    "current_statement_audit": current["audit"],
                    "current_tracing_no": current_source.get("tracing_no", "legacy-oldletters"),
                    "current_publish_datetime_jalali": current_source["publish_datetime_jalali"],
                    "current_source_url": current_source["report_url"],
                    "previous_statement_months": previous_months or "",
                    "previous_statement_audit": previous["audit"] if previous else "",
                    "previous_tracing_no": previous_source.get("tracing_no", "legacy-oldletters") if previous_source else "",
                    "previous_source_url": previous_source["report_url"] if previous_source else "",
                }
            )
            availability.append(
                {
                    "fiscal_year_jalali": year_text,
                    "quarter": quarter,
                    "available": True,
                    "reason": "",
                }
            )

    if len(availability) != 80 or len(output) != 75:
        raise RuntimeError(
            f"Unexpected quarterly coverage: {len(output)} available of {len(availability)} expected"
        )
    if len({(row["fiscal_year_jalali"], row["quarter"]) for row in output}) != len(output):
        raise RuntimeError("Duplicate fiscal-year quarter")
    for row in output:
        if row["operating_revenue_million_irr"] <= 0:
            raise RuntimeError(f"Non-positive quarterly revenue in {row['fiscal_year_jalali']} Q{row['quarter']}")
        if row["gross_profit_million_irr"] > row["operating_revenue_million_irr"]:
            raise RuntimeError(f"Gross profit exceeds revenue in {row['fiscal_year_jalali']} Q{row['quarter']}")

    atomic_csv(OUTPUT_PATH, output)
    atomic_csv(AVAILABILITY_PATH, availability)
    return output, availability


def main() -> None:
    output, availability = build()
    wage_rows = sum(bool(row["wage_detail_available"]) for row in output)
    missing = sum(not bool(row["available"]) for row in availability)
    print(f"Built {len(output)} quarterly rows; {wage_rows} with wage detail; {missing} unavailable")


if __name__ == "__main__":
    main()
