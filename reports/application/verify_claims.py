"""Read local research outputs and reproduce the application evidence report.

No collectors run and no datasets are modified. --write updates only EVIDENCE.md.
Run from any directory; requires the root pandas/numpy dependencies and local data.
"""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
REPORT = Path(__file__).with_name("EVIDENCE.md")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def read(relative: str, keys: list[str], hashes: dict[str, str]) -> pd.DataFrame:
    path = ROOT / relative
    hashes[relative] = hashlib.sha256(path.read_bytes()).hexdigest()
    frame = pd.read_csv(path)
    require(not frame.empty, f"Empty input: {relative}")
    require(not frame[keys].isna().any().any(), f"Missing keys: {relative}")
    require(not frame.duplicated(keys).any(), f"Duplicate keys: {relative}")
    return frame


def verify_ratio(frame: pd.DataFrame, price: str, reference: str, result: str) -> None:
    values = frame[[price, reference, result]].to_numpy(dtype=float)
    require(np.isfinite(values).all(), f"Nonfinite values in {result}")
    require((frame[[price, reference]] > 0).all().all(), f"Nonpositive inputs: {result}")
    expected = 100 * (frame[price] / frame[reference] - 1)
    require(np.allclose(expected, frame[result], rtol=0, atol=1e-7), f"Formula mismatch: {result}")


def render() -> str:
    hashes: dict[str, str] = {}
    lines = [
        "# Application evidence checkpoint",
        "",
        "Prepared for the 2026-10-17 portfolio review from existing local outputs.",
        "Copper maintenance reconciled 2026-10-18; its primary sample is unchanged.",
        "This is a file and formula verification, not a source refresh, independent",
        "source audit, server check, or new execution of the allocation notebook.",
        "",
        "## Commodity certificate research",
        "",
        "Means and medians are unweighted across modeled certificate-trading days.",
        "The direct international comparison below uses exactly the primary sample dates.",
        "",
        "| Project | Primary dates | Rows | Observed anchors | Interpolated | Mean premium | Median premium | Same-sample certificate/LME–FX mean |",
        "|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    coverage = []
    for name in ("copper", "zinc"):
        base = f"commodity/{name}/data/processed/bubble"
        frame = read(f"{base}/{name}_certificate_bubble.csv", ["date"], hashes)
        direct = read(f"{base}/certificate_vs_intrinsic_bubble.csv", ["date"], hashes)
        physical = read(f"{base}/physical_vs_intrinsic_bubble.csv", ["date"], hashes)
        verify_ratio(frame, "certificate_price_irr_per_kg", "estimated_physical_price_irr_per_kg", "certificate_bubble_pct")
        verify_ratio(direct, "certificate_price_irr_per_kg", "intrinsic_price_irr_per_kg", "certificate_vs_intrinsic_bubble_pct")
        verify_ratio(physical, "physical_price_irr_per_kg", "intrinsic_price_irr_per_kg", "physical_vs_intrinsic_bubble_pct")
        for data in (frame, direct, physical):
            require(data.date.is_monotonic_increasing, f"Unsorted dates: {name}")
            pd.to_datetime(data.date, format="%Y-%m-%d", errors="raise")
            for source in ("lme_source_date", "usd_source_date"):
                require((data[source] <= data.date).all(), f"Future as-of input: {name}/{source}")
        observed = frame.physical_ratio_method.eq("observed")
        require(frame.physical_ratio_method.isin(["observed", "linear_interpolation"]).all(), f"Unknown estimator: {name}")
        require((frame.ratio_left_anchor_date <= frame.date).all() and (frame.ratio_right_anchor_date >= frame.date).all(), f"Unbounded estimate: {name}")
        anchor_dates = set(frame.loc[observed, "date"])
        require(frame.ratio_left_anchor_date.isin(anchor_dates).all() and frame.ratio_right_anchor_date.isin(anchor_dates).all(), f"Missing anchor: {name}")
        require(np.allclose(frame.loc[observed, "observed_physical_price_irr_per_kg"], frame.loc[observed, "estimated_physical_price_irr_per_kg"], rtol=0, atol=1e-6), f"Anchor reconstruction: {name}")
        paired = frame[["date"]].merge(direct, on="date", validate="one_to_one")
        require(len(paired) == len(frame), f"Incomplete common sample: {name}")
        premium = frame.certificate_bubble_pct
        lines.append(f"| {name.title()} | {frame.date.min()}–{frame.date.max()} | {len(frame)} | {observed.sum()} | {(~observed).sum()} | {premium.mean():.2f}% | {premium.median():.2f}% | {paired.certificate_vs_intrinsic_bubble_pct.mean():.2f}% |")
        coverage.append(f"- {name.title()}: direct certificate/intrinsic output has {len(direct)} rows through {direct.date.max()} (full-sample mean {direct.certificate_vs_intrinsic_bubble_pct.mean():.2f}%); physical/intrinsic output has {len(physical)} rows through {physical.date.max()}.")
    lines += ["", *coverage, "", "Interpolated observations may use later physical anchors. These are descriptive", "valuation estimates; neither predictive accuracy nor executable arbitrage is established.", "", "## Gold ETF research", "", "| Fund | Full-history matched fund-days | First matched date | Last matched date | Two-year candidate days | Exact NAV matches |", "|---|---:|---|---|---:|---:|"]
    total = 0
    for fund in ("ayar", "tala", "kahroba", "ganj", "gohar"):
        frame = read(f"commodity/gold/data/processed/bubble/{fund}_nav_bubble.csv", ["date"], hashes)
        window = read(f"commodity/gold/data/processed/analysis/{fund}_daily_price_nav_2y.csv", ["date"], hashes)
        verify_ratio(frame, "closing_price_irr", "redemption_nav_irr", "bubble_pct")
        require(frame.date.is_monotonic_increasing, f"Unsorted gold history: {fund}")
        require((frame.trade_volume > 0).all() and (frame.trade_count > 0).all(), f"Nontrading gold observation: {fund}")
        require(frame.fund.eq(fund).all(), f"Fund identity mismatch: {fund}")
        require(frame.alignment_method.eq("exact_date_close_to_redemption_nav").all(), f"Unexpected gold alignment: {fund}")
        require(frame.nav_provider.eq("fipiran_historical").all(), f"Unexpected NAV provider: {fund}")
        require(window.nav_available.isin([True, False]).all(), f"Invalid availability flag: {fund}")
        total += len(frame)
        lines.append(f"| {fund.title()} | {len(frame):,} | {frame.date.min()} | {frame.date.max()} | {len(window)} | {int(window.nav_available.sum())} |")
    lines += ["", f"Total: **{total:,} matched fund-day observations**, not {total:,} distinct calendar days.", "Counts refer to local CSVs. The server database and provider discrepancies were not", "re-audited for this review. Exact valuation-date matching does not prove NAV was", "available when the market price was observed.", "", "## Allocation and REIT scope", ""]
    base = "asset_allocation/data/processed/analysis"
    for filename, label in (("monthly_asset_levels.csv", "Level grid"), ("monthly_asset_returns.csv", "Return grid")):
        frame = read(f"{base}/{filename}", ["jalali_period", "asset_id"], hashes)
        require(frame.asset_id.nunique() == 4, "Allocation asset universe changed")
        lines.append(f"- {label}: {len(frame):,} asset-month rows; {frame.jalali_period.nunique()} calendar months, {frame.jalali_period.min()}–{frame.jalali_period.max()} (Solar Hijri).")
        if filename == "monthly_asset_returns.csv":
            missing = int(frame.monthly_return.isna().sum())
            aligned = frame.pivot(index="jalali_period", columns="asset_id", values="monthly_return").dropna()
            lines.append(f"  Missing return cells: {missing}; complete four-asset months: {len(aligned)}. Grid size is not the number of complete observations.")
    reits = read(f"{base}/reit_eight_fund_comparison.csv", ["ins_code"], hashes)
    require(reits.dividend_history_status.isin([
        "dividend_history_incomplete", "unverified_dividend_history",
        "provisional_dates_and_history_incomplete",
    ]).all(), "REIT dividend evidence status changed; review the stated scope")
    lines += [f"- REIT scenario summary: {len(reits)} funds, {int(reits.identified_dividend_events.sum())} identified events; latest close dates {reits.latest_trading_date.min()}–{reits.latest_trading_date.max()}.", "- All eight REIT histories remain labelled incomplete or unverified for dividends.", "- Historical portfolio optimization is an ex-post pilot. Expert-survey allocation", "  and an investable out-of-sample strategy are not delivered results.", "", "## Input fingerprints", "", "SHA-256 fingerprints pin the exact local derived files used for these claims.", "Raw third-party datasets are not included in the application package.", "", "| Local input (relative to repository root) | SHA-256 |", "|---|---|"]
    lines += [f"| `{path}` | `{digest}` |" for path, digest in hashes.items()]
    lines += ["", "## Recheck", "", "```powershell", "python reports/application/verify_claims.py --check", "```", "", "The command fails if a formula, identity, key, alignment, or fingerprint changes.", "After an intentional research refresh, review all public claims before regenerating", "this report with `--write`. This verifier does not establish source correctness,", "re-execute every model, or validate economic comparability.", ""]
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    report = render()
    if args.write:
        REPORT.write_text(report, encoding="utf-8")
        print(f"Wrote {REPORT}")
    elif args.check:
        require(REPORT.read_text(encoding="utf-8") == report, "Evidence checkpoint changed; review application claims before updating")
        print("Application evidence: formulas, keys, alignment, counts, and fingerprints verified")
    else:
        print(report)


if __name__ == "__main__":
    main()
