"""Build the canonical daily IME warehouse and assessment-fee panel."""

from __future__ import annotations

import csv
from datetime import date, timedelta
from pathlib import Path


CURRENT_URL = "https://www.ime.co.ir/WarehousesFee.html"
OUTPUT_COLUMNS = [
    "date",
    "commodity",
    "daily_storage_fee_rial",
    "storage_fee_basis",
    "storage_boundary_quality",
    "assessment_fee_rial",
    "assessment_fee_basis",
    "assessment_boundary_quality",
    "storage_source_url",
    "assessment_source_url",
]

# Assessment tariffs are separate from storage-fee events.  Older rows are
# observations of the official archived table; the final rows are the live table.
ASSESSMENT_STATES = [
    ("2019-04-18", "saffron", "1320000", "sample_max_4kg", "first_observed", "https://web.archive.org/web/20190418100538id_/https://www.ime.co.ir/hazine-anbardari.html"),
    ("2019-04-18", "gold_coin", "20000", "coin", "first_observed", "https://web.archive.org/web/20190418100538id_/https://www.ime.co.ir/hazine-anbardari.html"),
    ("2019-08-18", "green_cumin", "12500", "kg", "first_observed", "https://web.archive.org/web/20190818155404id_/https://www.ime.co.ir/hazine-anbardari.html"),
    ("2020-01-21", "pistachio", "1500", "kg", "first_observed", "https://web.archive.org/web/20200121124235id_/http://www.ime.co.ir/hazine-anbardari.html"),
    ("2021-01-21", "raisin", "90", "kg", "first_observed", "https://web.archive.org/web/20210121084803id_/https://www.ime.co.ir/hazine-anbardari.html"),
    ("2021-01-21", "saffron", "3200000", "sample_max_4kg", "first_observed", "https://web.archive.org/web/20210121084803id_/https://www.ime.co.ir/hazine-anbardari.html"),
    ("2021-01-21", "gold_coin", "30000", "coin", "first_observed", "https://web.archive.org/web/20210121084803id_/https://www.ime.co.ir/hazine-anbardari.html"),
    ("2021-01-21", "green_cumin", "12500", "kg", "first_observed", "https://web.archive.org/web/20210121084803id_/https://www.ime.co.ir/hazine-anbardari.html"),
    ("2021-01-21", "pistachio", "2000", "kg", "first_observed", "https://web.archive.org/web/20210121084803id_/https://www.ime.co.ir/hazine-anbardari.html"),
    ("2021-01-21", "date_fruit", "2000", "kg", "first_observed", "https://web.archive.org/web/20210121084803id_/https://www.ime.co.ir/hazine-anbardari.html"),
    ("2021-04-12", "rice", "700", "kg", "first_observed", "https://web.archive.org/web/20210412072321id_/https://www.ime.co.ir/hazine-anbardari.html"),
    ("2021-09-26", "raisin", "1000", "kg", "first_observed", "https://web.archive.org/web/20210926223105id_/https://www.ime.co.ir/hazine-anbardari.html"),
    ("2022-01-25", "copper_cathode", "0", "none", "first_observed", "https://web.archive.org/web/20220125175931id_/https://www.ime.co.ir/hazine-anbardari.html"),
    ("2022-01-25", "rice", "1000", "kg", "first_observed", "https://web.archive.org/web/20220125175931id_/https://www.ime.co.ir/hazine-anbardari.html"),
    ("2022-01-25", "raisin", "90", "kg", "first_observed", "https://web.archive.org/web/20220125175931id_/https://www.ime.co.ir/hazine-anbardari.html"),
    ("2022-01-25", "saffron", "4200000", "sample_max_4kg", "first_observed", "https://web.archive.org/web/20220125175931id_/https://www.ime.co.ir/hazine-anbardari.html"),
    ("2022-01-25", "green_cumin", "18000", "kg", "first_observed", "https://web.archive.org/web/20220125175931id_/https://www.ime.co.ir/hazine-anbardari.html"),
    ("2022-01-25", "pistachio", "3000", "kg", "first_observed", "https://web.archive.org/web/20220125175931id_/https://www.ime.co.ir/hazine-anbardari.html"),
    ("2022-05-21", "chickpea", "90", "kg", "first_observed", "https://web.archive.org/web/20220521181324id_/https://www.ime.co.ir/hazine-anbardari.html"),
    ("2023-09-22", "iron_ore", "0", "none", "first_observed", "https://web.archive.org/web/20230922053608id_/https://www.ime.co.ir/hazine-anbardari.html"),
    ("2023-09-22", "quarter_gold_coin", "0", "none", "first_observed", "https://web.archive.org/web/20230922053608id_/https://www.ime.co.ir/hazine-anbardari.html"),
    ("2023-09-22", "gold_coin", "117000", "coin", "first_observed", "https://web.archive.org/web/20230922053608id_/https://www.ime.co.ir/hazine-anbardari.html"),
    ("2023-09-22", "saffron", "5500000", "sample_max_4kg", "first_observed", "https://web.archive.org/web/20230922053608id_/https://www.ime.co.ir/hazine-anbardari.html"),
    ("2023-09-22", "gold_bullion", "40000000", "bar", "first_observed", "https://web.archive.org/web/20230922053608id_/https://www.ime.co.ir/hazine-anbardari.html"),
    ("2023-09-22", "pistachio", "20000", "kg", "first_observed", "https://web.archive.org/web/20230922053608id_/https://www.ime.co.ir/hazine-anbardari.html"),
    ("2026-08-11", "gold_coin", "375000", "coin", "current_table", CURRENT_URL),
    ("2026-08-11", "saffron", "10000000", "sample_max_4kg", "current_table", CURRENT_URL),
    ("2026-08-11", "gold_bullion", "90000000", "bar", "current_table", CURRENT_URL),
    ("2026-08-11", "silver_bullion", "3600000", "bar", "current_table", CURRENT_URL),
    ("2026-08-11", "copper_cathode", "0", "none", "current_table", CURRENT_URL),
    ("2026-08-11", "zinc_ingot", "0", "none", "current_table", CURRENT_URL),
    ("2026-08-11", "rebar", "0", "none", "current_table", CURRENT_URL),
    ("2026-08-11", "iron_ore_pellet", "0", "none", "current_table", CURRENT_URL),
    ("2026-08-11", "bitumen_60_70", "0", "none", "current_table", CURRENT_URL),
    ("2026-08-11", "vehicle", "0", "none", "current_table", CURRENT_URL),
    ("2026-08-11", "lead_ingot", "0", "none", "current_table", CURRENT_URL),
]


def _read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def _validate_states(states: dict[str, list[dict[str, str]]], label: str) -> None:
    if not states:
        raise ValueError(f"No {label} states were loaded")
    for commodity, rows in states.items():
        if not commodity or not rows:
            raise ValueError(f"Invalid {label} state group: {commodity!r}")
        for row in rows:
            date.fromisoformat(row["date"])
            if not row["fee"] or not row["basis"] or not row["source"]:
                raise ValueError(f"Incomplete {label} state: {row!r}")


def build(project_dir: Path, through: date | None = None) -> Path:
    through = through or date.today()
    interim = project_dir / "data" / "interim"
    storage: dict[str, list[dict[str, str]]] = {}

    # Older archived tables establish a first-observed boundary.
    for row in _read(interim / "historical_page_observations.csv"):
        storage.setdefault(row["commodity"], []).append({
            "date": row["observed_at"], "fee": row["daily_fee_rial"],
            "basis": row["fee_basis"], "quality": "first_observed",
            "source": row["source_url"],
        })
    # Exact official notices override an observation on the same date.
    for row in _read(interim / "warehouse_fee_events.csv"):
        storage.setdefault(row["commodity"], []).append({
            "date": row["effective_from"], "fee": row["daily_fee_rial"],
            "basis": row["fee_basis"], "quality": "exact_effective_date",
            "source": row["source_pdf_url"] or row["source_page_url"],
        })
    _validate_states(storage, "storage-fee")

    assessments: dict[str, list[dict[str, str]]] = {}
    for effective, commodity, fee, basis, quality, source in ASSESSMENT_STATES:
        assessments.setdefault(commodity, []).append({
            "date": effective, "fee": fee, "basis": basis,
            "quality": quality, "source": source,
        })
    _validate_states(assessments, "assessment-fee")

    output_rows = []
    for commodity, raw_states in storage.items():
        by_date: dict[str, dict[str, str]] = {}
        for state in sorted(raw_states, key=lambda item: (item["date"], item["quality"])):
            previous = by_date.get(state["date"])
            if previous is None or state["quality"] == "exact_effective_date":
                by_date[state["date"]] = state
        states = sorted(by_date.values(), key=lambda item: item["date"])
        assessment_states = sorted(assessments.get(commodity, []), key=lambda item: item["date"])
        start = date.fromisoformat(states[0]["date"])
        cursor = start
        storage_index = 0
        assessment_index = -1
        while cursor <= through:
            iso = cursor.isoformat()
            while storage_index + 1 < len(states) and states[storage_index + 1]["date"] <= iso:
                storage_index += 1
            while assessment_index + 1 < len(assessment_states) and assessment_states[assessment_index + 1]["date"] <= iso:
                assessment_index += 1
            storage_state = states[storage_index]
            assessment = assessment_states[assessment_index] if assessment_index >= 0 else None
            output_rows.append({
                "date": iso,
                "commodity": commodity,
                "daily_storage_fee_rial": storage_state["fee"],
                "storage_fee_basis": storage_state["basis"],
                "storage_boundary_quality": storage_state["quality"],
                "assessment_fee_rial": assessment["fee"] if assessment else "",
                "assessment_fee_basis": assessment["basis"] if assessment else "unknown",
                "assessment_boundary_quality": assessment["quality"] if assessment else "not_recovered",
                "storage_source_url": storage_state["source"],
                "assessment_source_url": assessment["source"] if assessment else "",
            })
            cursor += timedelta(days=1)

    output_rows.sort(key=lambda row: (row["date"], row["commodity"]))
    keys = [(row["date"], row["commodity"]) for row in output_rows]
    if len(keys) != len(set(keys)):
        raise ValueError("Duplicate date/commodity rows in final daily panel")
    output = project_dir / "data" / "processed" / "warehouse_fees_daily.csv"
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_suffix(".csv.tmp")
    with temporary.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=OUTPUT_COLUMNS)
        writer.writeheader()
        writer.writerows(output_rows)
    temporary.replace(output)
    print(f"Saved {len(output_rows)} rows for {len(storage)} commodities through {through}: {output}")
    return output


if __name__ == "__main__":
    build(Path(__file__).resolve().parents[2])
