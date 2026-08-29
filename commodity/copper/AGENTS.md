# Agent project notes

## Scope

Keep copper-specific work inside `commodity/copper/`. Shared collector changes
belong in `shared/ime_data/` and must remain compatible with all commodities.

## Agreed workflow

1. `src/copper/collectors/lme.py` owns downloading and raw-data persistence.
2. First run collects all Westmetall copper history from 2008 onward.
3. Subsequent runs are incremental: refresh the newest locally stored year
   through the current year, merge by ISO date, and retain older history.
4. Preserve source HTML in `data/raw/lme/html_snapshots/`.
5. Store the notebook-friendly raw table at
   `data/raw/lme/copper_lme_raw.csv` without numeric cleaning.
6. Use `notebooks/01_lme_analysis.ipynb` for exploration and processing only.
7. Store physical derivatives in `data/processed/physical`, certificate-only derivatives in
   `data/processed/certificate`, bubble/model outputs in `data/processed/bubble`, and other
   analytical tables in `data/processed/analysis`.
8. Preserve raw files and do not silently weaken validation checks.
9. `src/copper/collectors/fx.py` incrementally extends `data/raw/fx/usd_to_rial.csv`
   from TGJU. Preserve user-supplied historical rows and merge by Persian date.
   Store new TGJU observations using the daily closing price in `price_irr`, retain
   unavailable historical values as `legacy_high_low_midpoint`, record the method
   in `price_method`, and validate calendar conversion.

## Source contract

- URL: `https://www.westmetall.com/en/markdaten.php`
- Query: `action=table`, `field=LME_Cu_cash`, `year=YYYY`
- Expected fields: date, cash settlement, three-month price, and stock.
- The page repeats header rows between months; these are not observations.

## Before changing the crawler

Run the script, confirm the CSV contains unique sorted ISO dates, and confirm a
second run refreshes only the newest year rather than downloading from 2008.
Keep the implementation dependency-free unless a new dependency has a clear,
documented benefit.

## Certificate and physical market

Detailed certificate safeguards and the approved physical scope are in
`docs/CERTIFICATE_POLICY.md`. Keep certificate and physical raw data under
`data/raw/{certificate,physical}` and derived outputs under their `data/processed/*` domain.
Update `docs/WORKFLOW.md` after source, schema, formula, path, or row-count changes.
