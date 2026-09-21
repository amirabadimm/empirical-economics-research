"""One-command, project-local certificate/physical Power BI refresh.

Uses local raw inputs; run the documented collectors separately to fetch new data.
"""
from __future__ import annotations

import csv
import subprocess
import sys
from decimal import Decimal
from pathlib import Path


PROJECT = Path(__file__).resolve().parent
NAME = PROJECT.name
BUILDERS = {
    "copper": ["src/copper/processing/build_physical_benchmark.py", "src/copper/processing/build_certificate_bubble.py", "src/copper/processing/build_intrinsic_bubbles.py", "src/copper/processing/build_bubble_distribution.py"],
    "zinc": ["src/zinc/processing/build_physical_benchmark.py", "src/zinc/processing/build_certificate_bubble.py", "src/zinc/processing/build_intrinsic_bubbles.py", "src/zinc/processing/build_bubble_distribution.py"],
    "pellet": ["src/pellet/processing/build_certificate_bubble.py", "src/pellet/processing/build_bubble_distribution.py"],
    "rebar": ["src/rebar/processing/build_a3_18_exact_bubble.py", "src/rebar/processing/build_a3_12_exact_bubble.py", "src/rebar/processing/build_bubble_distribution.py"],
    "pista": ["analysis/build_certificate_bubble.py", "analysis/build_bubble_distribution.py"],
}
SOURCES = {
    "copper": [("primary", "copper_certificate_bubble.csv")],
    "zinc": [("primary", "zinc_certificate_bubble.csv")],
    "pellet": [("gol_gohar_gohar_zamin", "pellet_certificate_bubble.csv")],
    "rebar": [("a3_18", "rebar_a3_18_exact_date_bubble.csv"), ("a3_12_sensitivity", "rebar_a3_12_exact_date_bubble.csv")],
    "pista": [("dahan_bast_weekly_alignment", "pista_certificate_bubble.csv")],
}
COLUMNS = ["commodity", "comparison", "date", "date_jalali", "physical_date", "physical_age_days", "certificate_price_irr_per_kg", "physical_price_irr_per_kg", "spread_irr_per_kg", "premium_discount_pct", "certificate_trades_volume", "physical_price_method", "comparability_status", "physical_product_scope"]


def pick(row: dict[str, str], *keys: str) -> str:
    return next((row[key] for key in keys if row.get(key, "") != ""), "")


def convert(comparison: str, row: dict[str, str]) -> dict[str, str]:
    date = pick(row, "date", "certificate_date")
    certificate = pick(row, "certificate_price_irr_per_kg", "certificate_irr_per_kg")
    physical = pick(row, "estimated_physical_price_irr_per_kg", "physical_price_irr_per_kg", "physical_mid_irr_per_kg")
    if not date or not certificate or not physical:
        raise ValueError("Missing date or price")
    c, p = Decimal(certificate), Decimal(physical)
    if c <= 0 or p <= 0:
        raise ValueError(f"Nonpositive price on {date}")
    method = pick(row, "physical_ratio_method", "alignment_method", "physical_price_method")
    status = pick(row, "comparability_status")
    if NAME in ("copper", "zinc"):
        status = "approved_benchmark_bounded_valuation"
    elif NAME == "pellet":
        status = "exploratory_producer_composition_risk"
    elif NAME == "pista":
        status = "provisional_unverified_unit_and_product_match"
        method = "latest_weekly_quote_max_6_days"
    exact = NAME == "pellet" or method == "observed" or method.startswith("exact_date")
    return {
        "commodity": "pistachio" if NAME == "pista" else NAME,
        "comparison": comparison, "date": date,
        "date_jalali": pick(row, "date_jalali", "certificate_date_jalali"),
        "physical_date": pick(row, "physical_date") if NAME == "pista" else (date if exact else ""),
        "physical_age_days": pick(row, "physical_age_days") if NAME == "pista" else ("0" if exact else ""),
        "certificate_price_irr_per_kg": certificate,
        "physical_price_irr_per_kg": physical,
        "spread_irr_per_kg": str(c - p),
        "premium_discount_pct": str((c / p - 1) * 100),
        "certificate_trades_volume": pick(row, "certificate_trades_volume", "certificate_trades_volume_source_units"),
        "physical_price_method": method,
        "comparability_status": status,
        "physical_product_scope": pick(row, "physical_product_scope") or ("Dahan-Bast weekly quote" if NAME == "pista" else ""),
    }


def main() -> None:
    if NAME not in BUILDERS:
        raise ValueError(f"Unsupported project: {NAME}")
    for relative in BUILDERS[NAME]:
        subprocess.run([sys.executable, str(PROJECT / relative)], cwd=PROJECT, check=True)
    rows = []
    for comparison, filename in SOURCES[NAME]:
        with (PROJECT / "data/processed/bubble" / filename).open(encoding="utf-8-sig", newline="") as handle:
            source = list(csv.DictReader(handle))
        if not source:
            raise ValueError(f"Empty source: {filename}")
        dates = [pick(row, "date", "certificate_date") for row in source]
        if len(dates) != len(set(dates)):
            raise ValueError(f"Duplicate dates: {filename}")
        rows.extend(convert(comparison, row) for row in source)
    rows.sort(key=lambda row: (row["comparison"], row["date"]))
    destination = PROJECT / "outputs/power_bi" / f"{NAME}_certificate_physical_comparison.csv"
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_suffix(".csv.tmp")
    with temporary.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=COLUMNS)
        writer.writeheader()
        writer.writerows(rows)
    temporary.replace(destination)
    print(f"{len(rows)} rows: {destination}")


if __name__ == "__main__":
    main()
