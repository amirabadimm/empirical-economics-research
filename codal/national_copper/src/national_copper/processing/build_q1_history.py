"""Build a validated history from National Copper unaudited three-month filings."""

from __future__ import annotations

import csv
import hashlib
import json
import os
import re
import tempfile
import unicodedata
from pathlib import Path

import pandas as pd
from bs4 import BeautifulSoup


PROJECT_ROOT = Path(__file__).resolve().parents[3]
INDEX_PATH = PROJECT_ROOT / "data" / "raw" / "financial_statements" / "q1_filing_index.csv"
OUTPUT_PATH = PROJECT_ROOT / "data" / "processed" / "national_copper_q1_financials.csv"

PERSIAN_DIGITS = str.maketrans("۰۱۲۳۴۵۶۷۸۹", "0123456789")
ARABIC_DIGITS = str.maketrans("٠١٢٣٤٥٦٧٨٩", "0123456789")


def normalize_text(value: object) -> str:
    text = unicodedata.normalize("NFKC", str(value or ""))
    text = text.replace("ي", "ی").replace("ك", "ک").replace("ة", "ه")
    text = text.translate(PERSIAN_DIGITS).translate(ARABIC_DIGITS)
    text = re.sub(r"[\u200c\u200e\u200f\u202a-\u202e]", " ", text)
    text = re.sub(r"[^0-9A-Za-zآ-ی]+", " ", text)
    return " ".join(text.split())


def parse_number(value: object) -> int:
    text = str(value).strip().translate(PERSIAN_DIGITS).translate(ARABIC_DIGITS)
    negative = text.startswith("(") and text.endswith(")")
    text = text.replace(",", "").replace("٬", "").replace("(", "").replace(")", "")
    if not re.fullmatch(r"-?\d+(?:\.0+)?", text):
        raise ValueError(f"Not an integer financial value: {value!r}")
    result = int(float(text))
    return -abs(result) if negative else result


def row_cells(row) -> list[str]:
    return [cell.get_text(" ", strip=True) for cell in row.find_all(["th", "td"], recursive=False)]


def find_container(soup: BeautifulSoup, *title_fragments: str):
    expected = [normalize_text(fragment) for fragment in title_fragments]
    for container in soup.select("div.table-containet"):
        title_node = container.select_one(".table-title")
        title = normalize_text(title_node.get_text(" ", strip=True) if title_node else "")
        if all(fragment in title for fragment in expected):
            return container
    raise ValueError(f"Missing table whose title contains {title_fragments!r}")


def find_income_container(soup: BeautifulSoup):
    for container in soup.select("div.table-containet"):
        title_node = container.select_one(".table-title")
        title = normalize_text(title_node.get_text(" ", strip=True) if title_node else "")
        if "صورت سود" in title and "زیان" in title and "تلفیقی" not in title:
            return container
    raise ValueError("Missing standalone income statement")


def find_container_exact(soup: BeautifulSoup, title: str):
    expected = normalize_text(title)
    for container in soup.select("div.table-containet"):
        title_node = container.select_one(".table-title")
        actual = normalize_text(title_node.get_text(" ", strip=True) if title_node else "")
        if actual == expected:
            return container
    raise ValueError(f"Missing table titled {title!r}")


def find_row(container, labels: tuple[str, ...]) -> list[str]:
    normalized_labels = tuple(normalize_text(label) for label in labels)
    matches: list[list[str]] = []
    for row in container.select("tbody tr"):
        cells = row_cells(row)
        if not cells:
            continue
        label = normalize_text(cells[0])
        if label in normalized_labels:
            matches.append(cells)
    if len(matches) != 1:
        raise ValueError(f"Expected one row for {labels!r}; found {len(matches)}")
    return matches[0]


def validate_html_audit(soup: BeautifulSoup, period: str, required_audit: str) -> None:
    income = find_income_container(soup)
    header = normalize_text(income.select_one("thead").get_text(" ", strip=True))
    if normalize_text(period) not in header or normalize_text(required_audit) not in header:
        raise ValueError(f"Current column for {period} is not explicitly {required_audit}")


def parse_html(
    path: Path, period: str, required_audit: str = "حسابرسی نشده"
) -> dict[str, int | None]:
    soup = BeautifulSoup(path.read_text(encoding="utf-8"), "html.parser")
    if not soup.select("div.table-containet"):
        if "var datasource =" in path.read_text(encoding="utf-8"):
            return parse_datasource_html(path, period, required_audit)
        return parse_legacy_html(soup, period, required_audit)
    validate_html_audit(soup, period, required_audit)
    income = find_income_container(soup)
    revenue = find_row(income, ("درآمدهای عملیاتی", "درآمدهاي عملياتي"))
    gross = find_row(income, ("سود زیان ناخالص",))
    net = find_row(income, ("سود زیان خالص",))
    result: dict[str, int | None] = {
        "operating_revenue_million_irr": parse_number(revenue[1]),
        "gross_profit_million_irr": parse_number(gross[1]),
        "net_profit_million_irr": parse_number(net[1]),
        "direct_labor_cost_million_irr": None,
        "overhead_wages_million_irr": None,
        "sga_wages_million_irr": None,
        "other_overhead_expense_million_irr": None,
        "other_sga_expense_million_irr": None,
    }

    try:
        cost = find_container_exact(soup, "بهای تمام شده")
        direct = find_row(cost, ("دستمزد مستقیم تولید", "دستمزدمستقیم تولید"))
        result["direct_labor_cost_million_irr"] = parse_number(direct[2])

        overhead = None
        for fragments in (("سربار", "عمومی", "اداری"), ("هزینه های سربار", "عمومی", "اداری")):
            try:
                overhead = find_container(soup, *fragments)
                break
            except ValueError:
                pass
        if overhead is None:
            raise ValueError("Missing overhead and SG&A detail table")
        wages = find_row(overhead, ("هزینه حقوق و دستمزد",))
        other = find_row(overhead, ("سایر هزینه ها", "سایر هزینه ها "))
        if len(wages) < 7 or len(other) < 7:
            raise ValueError("Unexpected overhead/SG&A table shape")
        result["overhead_wages_million_irr"] = parse_number(wages[2])
        result["sga_wages_million_irr"] = parse_number(wages[5])
        result["other_overhead_expense_million_irr"] = parse_number(other[2])
        result["other_sga_expense_million_irr"] = parse_number(other[5])
    except ValueError:
        # Codal did not publish these detailed schedules in every historical export.
        pass
    return result


def parse_datasource_html(
    path: Path, period: str, required_audit: str = "حسابرسی نشده"
) -> dict[str, int | None]:
    text = path.read_text(encoding="utf-8")
    match = re.search(r"var datasource = (\{.*?\});\s*(?:\r?\n|$)", text, flags=re.DOTALL)
    if not match:
        raise ValueError("Missing structured datasource JSON")
    datasource = json.loads(match.group(1))
    expected_audited = required_audit == "حسابرسی شده"
    if str(datasource.get("periodEndToDate")) != period:
        raise ValueError(f"Datasource period mismatch for {period}")
    if bool(datasource.get("isAudited")) != expected_audited:
        raise ValueError(f"Datasource is not explicitly {required_audit}")

    income_table = None
    for sheet in datasource.get("sheets", []):
        for table in sheet.get("tables", []):
            if table.get("aliasName") == "IncomeStatement":
                income_table = table
                break
    if income_table is None:
        raise ValueError("Datasource has no income statement")

    labels: dict[int, str] = {}
    values: dict[int, int] = {}
    for cell in income_table.get("cells", []):
        if cell.get("cellGroupName") != "Body" or not cell.get("isVisible", True):
            continue
        row_code = int(cell["rowCode"])
        column = int(cell["columnSequence"])
        if column == 1:
            labels[row_code] = normalize_text(cell.get("value"))
        elif column == 2 and str(cell.get("periodEndToDate")) == period:
            try:
                values[row_code] = parse_number(cell.get("value"))
            except ValueError:
                pass

    def metric(label_options: tuple[str, ...]) -> int:
        expected = {normalize_text(label) for label in label_options}
        matches = [values[row] for row, label in labels.items() if label in expected and row in values]
        if len(matches) != 1:
            raise ValueError(f"Expected one datasource row for {label_options!r}; found {len(matches)}")
        return matches[0]

    return {
        "operating_revenue_million_irr": metric(("درآمدهای عملیاتی",)),
        "gross_profit_million_irr": metric(("سود زیان ناخالص",)),
        "net_profit_million_irr": metric(("سود زیان خالص",)),
        "direct_labor_cost_million_irr": None,
        "overhead_wages_million_irr": None,
        "sga_wages_million_irr": None,
        "other_overhead_expense_million_irr": None,
        "other_sga_expense_million_irr": None,
    }


def parse_legacy_html(
    soup: BeautifulSoup, period: str, required_audit: str = "حسابرسی نشده"
) -> dict[str, int | None]:
    full_text = normalize_text(soup.get_text(" ", strip=True))
    if normalize_text(period) not in full_text or normalize_text(required_audit) not in full_text:
        raise ValueError(f"Legacy HTML does not identify {period} as {required_audit}")

    def value_for(labels: tuple[str, ...]) -> int:
        normalized_labels = {normalize_text(label) for label in labels}
        matches: list[int] = []
        for row in soup.find_all("tr"):
            cells = row_cells(row)
            if cells and normalize_text(cells[0]) in normalized_labels and len(cells) > 1:
                try:
                    matches.append(parse_number(cells[1]))
                except ValueError:
                    pass
        if not matches:
            raise ValueError(f"Missing legacy HTML row for {labels!r}")
        return matches[0]

    return {
        "operating_revenue_million_irr": value_for(("درآمدهای عملیاتی",)),
        "gross_profit_million_irr": value_for(("سود زیان ناخالص",)),
        "net_profit_million_irr": value_for(("سود زیان خالص",)),
        "direct_labor_cost_million_irr": None,
        "overhead_wages_million_irr": None,
        "sga_wages_million_irr": None,
        "other_overhead_expense_million_irr": None,
        "other_sga_expense_million_irr": None,
    }


def xls_row_label(row: pd.Series) -> tuple[int, str] | None:
    candidates: list[tuple[int, str]] = []
    for column, value in row.items():
        if pd.isna(value) or isinstance(value, (int, float)):
            continue
        text = normalize_text(value)
        if text:
            candidates.append((int(column), text))
    return max(candidates, default=None, key=lambda item: item[0])


def find_xls_value(frame: pd.DataFrame, labels: tuple[str, ...]) -> int:
    normalized = {normalize_text(label) for label in labels}
    matches: list[int] = []
    for _, row in frame.iterrows():
        label = xls_row_label(row)
        if not label or label[1] not in normalized:
            continue
        numeric_columns = [
            int(column)
            for column, value in row.items()
            if int(column) < label[0]
            and pd.notna(value)
            and re.search(r"\d", str(value).translate(PERSIAN_DIGITS).translate(ARABIC_DIGITS))
        ]
        if not numeric_columns:
            continue
        value_column = max(numeric_columns)
        if pd.notna(row.iloc[value_column]):
            try:
                matches.append(parse_number(row.iloc[value_column]))
            except ValueError:
                pass
    if not matches:
        raise ValueError(f"Missing XLS row for {labels!r}")
    return matches[0]


def parse_xls(
    path: Path, period: str, required_audit: str = "حسابرسی نشده"
) -> dict[str, int | None]:
    frame = pd.read_excel(path, header=None, dtype=object)
    normalized_all = normalize_text(" ".join(str(value) for value in frame.to_numpy().ravel()))
    if normalize_text(period) not in normalized_all or normalize_text(required_audit) not in normalized_all:
        raise ValueError(f"XLS does not explicitly identify {period} as {required_audit}")

    revenue = find_xls_value(
        frame,
        ("درآمدهای عملیاتی", "فروش", "فروش خالص", "درآمد حاصل از فروش و ارائه خدمات"),
    )
    gross = find_xls_value(frame, ("سود زیان ناخالص",))
    net = find_xls_value(
        frame,
        ("سود زیان خالص", "سود زیان خالص پس از کسر مالیات", "سود خالص پس از کسر مالیات"),
    )
    return {
        "operating_revenue_million_irr": revenue,
        "gross_profit_million_irr": gross,
        "net_profit_million_irr": net,
        "direct_labor_cost_million_irr": None,
        "overhead_wages_million_irr": None,
        "sga_wages_million_irr": None,
        "other_overhead_expense_million_irr": None,
        "other_sga_expense_million_irr": None,
    }


def atomic_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    handle, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(handle, "w", newline="", encoding="utf-8-sig") as stream:
            writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)
        os.replace(temporary_name, path)
    except Exception:
        Path(temporary_name).unlink(missing_ok=True)
        raise


def build() -> list[dict[str, object]]:
    with INDEX_PATH.open(encoding="utf-8-sig", newline="") as stream:
        index = list(csv.DictReader(stream))
    latest: dict[str, dict[str, str]] = {}
    for row in index:
        period = row["period_end_jalali"]
        if period not in latest or row["publish_datetime_jalali"] > latest[period]["publish_datetime_jalali"]:
            latest[period] = row

    rows: list[dict[str, object]] = []
    for period, source in sorted(latest.items()):
        snapshot = PROJECT_ROOT / source["snapshot_path"]
        if hashlib.sha256(snapshot.read_bytes()).hexdigest() != source["snapshot_sha256"]:
            raise RuntimeError(f"Snapshot hash mismatch for {snapshot.name}")
        try:
            metrics = (
                parse_html(snapshot, period) if snapshot.suffix == ".html" else parse_xls(snapshot, period)
            )
        except Exception as error:
            raise RuntimeError(f"Failed to parse {period} from {snapshot.name}: {error}") from error
        rows.append(
            {
                "period_end_jalali": period,
                **metrics,
                "wage_detail_available": metrics["direct_labor_cost_million_irr"] is not None,
                "labor_data_status": (
                    "provisional_pending_header_mapping_and_reconciliation"
                    if metrics["direct_labor_cost_million_irr"] is not None
                    else "not_disclosed"
                ),
                "audit_status": "حسابرسی نشده",
                "is_correction": source["is_correction"],
                "tracing_no": source["tracing_no"],
                "publish_datetime_jalali": source["publish_datetime_jalali"],
                "source_title": source["title"],
                "source_url": source["report_url"],
                "source_snapshot_sha256": source["snapshot_sha256"],
            }
        )

    if len(rows) != 20 or rows[0]["period_end_jalali"] != "1386/03/31" or rows[-1]["period_end_jalali"] != "1405/03/31":
        raise RuntimeError("Unexpected Q1 period coverage")
    if len({row["period_end_jalali"] for row in rows}) != len(rows):
        raise RuntimeError("Duplicate Q1 periods")
    for row in rows:
        if row["audit_status"] != "حسابرسی نشده":
            raise RuntimeError("A non-unaudited observation entered the output")
        if row["operating_revenue_million_irr"] <= 0:
            raise RuntimeError(f"Non-positive revenue in {row['period_end_jalali']}")
        if row["gross_profit_million_irr"] > row["operating_revenue_million_irr"]:
            raise RuntimeError(f"Gross profit exceeds revenue in {row['period_end_jalali']}")
        wage_values = [
            row["direct_labor_cost_million_irr"],
            row["overhead_wages_million_irr"],
            row["sga_wages_million_irr"],
            row["other_overhead_expense_million_irr"],
            row["other_sga_expense_million_irr"],
        ]
        if bool(row["wage_detail_available"]) != all(value is not None for value in wage_values):
            raise RuntimeError(f"Partial detailed-cost schedule in {row['period_end_jalali']}")
    expected_corrections = {"1400/03/31", "1402/03/31", "1405/03/31"}
    actual_corrections = {str(row["period_end_jalali"]) for row in rows if row["is_correction"] == "True"}
    if actual_corrections != expected_corrections:
        raise RuntimeError(f"Unexpected correction selection: {sorted(actual_corrections)}")
    atomic_csv(OUTPUT_PATH, rows)
    return rows


def main() -> None:
    rows = build()
    wage_rows = sum(bool(row["wage_detail_available"]) for row in rows)
    print(f"Built {len(rows)} Q1 rows; wage schedules available for {wage_rows} rows")


if __name__ == "__main__":
    main()
