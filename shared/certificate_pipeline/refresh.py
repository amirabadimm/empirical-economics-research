"""One-command, project-local certificate/physical Power BI refresh.

Uses local raw inputs; run the documented collectors separately to fetch new data.
"""
from __future__ import annotations

import argparse
import json
import shutil
import csv
import subprocess
import sys
from decimal import Decimal
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PROJECTS = {name: "commodity/" + name for name in ("copper", "zinc", "pellet", "rebar", "bitumen")}
PROJECTS["pista"] = "goods/pista"

COLUMNS = ["commodity", "comparison", "date", "date_jalali", "physical_date", "physical_age_days", "certificate_price_irr_per_kg", "physical_price_irr_per_kg", "spread_irr_per_kg", "premium_discount_pct", "certificate_trades_volume", "physical_price_method", "comparability_status", "physical_product_scope"]


def pick(row: dict[str, str], *keys: str) -> str:
    return next((row[key] for key in keys if row.get(key, "") != ""), "")


def convert(name: str, comparison: str, row: dict[str, str]) -> dict[str, str]:
    date = pick(row, "date", "certificate_date")
    certificate = pick(row, "certificate_price_irr_per_kg", "certificate_irr_per_kg")
    physical = pick(row, "estimated_physical_price_irr_per_kg", "physical_price_irr_per_kg", "physical_mid_irr_per_kg")
    if not date or not certificate or not physical:
        raise ValueError("Missing date or price")
    c, p = Decimal(certificate), Decimal(physical)
    if not c.is_finite() or not p.is_finite() or c <= 0 or p <= 0:
        raise ValueError(f"Nonpositive price on {date}")
    spread, premium = str(c - p), str((c / p - 1) * 100)
    if name == "copper":
        # The production valuation owns these results; recomputation is a check only.
        for key, expected in [("certificate_bubble_irr_per_kg", spread),
                              ("certificate_bubble_pct", premium)]:
            value = Decimal(row[key])
            if not value.is_finite() or abs(value - Decimal(expected)) > Decimal("0.000001"):
                raise ValueError(f"Inconsistent canonical {key} on {date}")
        spread = row["certificate_bubble_irr_per_kg"]
        premium = row["certificate_bubble_pct"]
    method = pick(row, "physical_ratio_method", "alignment_method", "physical_price_method")
    status = pick(row, "comparability_status")
    if name in ("copper", "zinc"):
        status = "approved_benchmark_bounded_valuation"
    elif name == "pellet":
        status = "exploratory_producer_composition_risk"
    elif name == "pista":
        status = "provisional_unverified_unit_and_product_match"
        method = "latest_weekly_quote_max_6_days"
    exact = name == "pellet" or method == "observed" or method.startswith("exact_date")
    return {
        "commodity": "pistachio" if name == "pista" else name,
        "comparison": comparison, "date": date,
        "date_jalali": pick(row, "date_jalali", "certificate_date_jalali"),
        "physical_date": pick(row, "physical_date") if name == "pista" else (date if exact else ""),
        "physical_age_days": pick(row, "physical_age_days") if name == "pista" else ("0" if exact else ""),
        "certificate_price_irr_per_kg": certificate,
        "physical_price_irr_per_kg": physical,
        "spread_irr_per_kg": spread,
        "premium_discount_pct": premium,
        "certificate_trades_volume": pick(row, "certificate_trades_volume", "certificate_trades_volume_source_units"),
        "physical_price_method": method,
        "comparability_status": status,
        "physical_product_scope": pick(row, "physical_product_scope") or ("Dahan-Bast weekly quote" if name == "pista" else ""),
    }


def load_config(name):
    project = ROOT / PROJECTS[name]
    return project, json.loads((project / "pipeline.json").read_text(encoding="utf-8"))


def plan(name, collect=False):
    project, config = load_config(name)
    steps = [(ROOT / p, ROOT) for p in config["collectors"]] if collect else []
    steps += [(project / p, project) for p in config["builders"]]
    for script, _ in steps:
        if not script.is_file():
            raise FileNotFoundError(script)
    return steps


def export(name):
    project, config = load_config(name)
    rows = []
    for comparison, filename in config["sources"]:
        path = project / "data/processed/bubble" / filename
        with path.open(encoding="utf-8-sig", newline="") as handle:
            source = list(csv.DictReader(handle))
        if not source:
            raise ValueError(f"Empty source: {path}")
        dates = [pick(row, "date", "certificate_date") for row in source]
        if len(dates) != len(set(dates)):
            raise ValueError(f"Duplicate dates: {path}")
        for row in source:
            converted = convert(name, comparison, row)
            rows.append(row if config.get("passthrough") else converted)
    rows.sort(key=lambda row: (row["comparison"], row["date"]))
    destination = project / "outputs/power_bi" / f"{name}_certificate_physical_comparison.csv"
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_suffix(".csv.tmp")
    if config.get("passthrough"):
        shutil.copyfile(path, temporary)
    else:
        with temporary.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=COLUMNS)
            writer.writeheader()
            writer.writerows(rows)
    temporary.replace(destination)
    print(f"{name}: {len(rows)} rows -> {destination}")
    return destination


def main(project_name=None):
    parser = argparse.ArgumentParser(description=__doc__)
    if project_name is None:
        parser.add_argument("project", choices=[*PROJECTS, "all"])
    parser.add_argument("--collect", action="store_true", help="Fetch sources before rebuilding.")
    parser.add_argument("--plan", action="store_true", help="Show steps without running them.")
    args = parser.parse_args()
    selected = project_name or args.project
    names = list(PROJECTS) if selected == "all" else [selected]
    plans = [(name, plan(name, args.collect)) for name in names]
    collected = set()
    for name, steps in plans:
        _, config = load_config(name)
        if args.collect and config.get("manual_input"):
            print(config["manual_input"])
        for script, cwd in steps:
            if cwd == ROOT and script in collected:
                continue
            print(f"{name}: {script.relative_to(ROOT)}", flush=True)
            if not args.plan:
                subprocess.run([sys.executable, str(script)], cwd=cwd, check=True)
            if cwd == ROOT:
                collected.add(script)
        if not args.plan:
            export(name)


if __name__ == "__main__":
    main()
