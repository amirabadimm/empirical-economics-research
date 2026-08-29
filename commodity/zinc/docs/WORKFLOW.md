# Zinc-Ingot Warehouse-Receipt Certificate: Research Workflow

Last reviewed: 2026-08-29

## Research objective

The project values the Iranian zinc-ingot warehouse receipt relative to a comparable domestic
physical basket and an LME–FX intrinsic proxy. It explicitly separates zinc ingot from zinc dust
and preserves grade composition in every benchmark observation.

## Data checkpoint

| Source | Coverage |
|---|---|
| Certificate | 268 calendar rows; 194 positive-trading days through 2026-08-27 |
| Broad physical zinc market | 6,325 rows; 3,512 positive trades through 1405/06/04 |
| LME cash zinc | 4,719 dates from 2008-01-02 through 2026-08-28 |
| Shared free-market USD/IRR | 13,079 dates through 1405/06/05 |
| Approved physical benchmark | 554 days through 2026-08-09 |

## Architecture and source governance

Commodity-specific collectors live in `src/zinc/collectors`; deterministic builders live in
`src/zinc/processing`; shared IME logic lives in `shared/ime_data`. Raw responses and snapshots are
content-addressed once in `shared/data/raw/ime/physical`; Zinc-local physical snapshots are frozen
pre-consolidation evidence. Shared LME and intrinsic-regression engines live under
`shared/market_data` and `shared/market_analysis`, with Zinc assumptions kept in local wrappers.
All raw sources are immutable, collectors are incremental and atomic, and analysis writes only to
interim or processed paths. Bulk data and source snapshots are excluded from Git.

The certificate collector validates the continuous zinc contract identity and uses
`TodaySettlementPrice` as the analytical price. The physical collector archives complete monthly
responses before applying the broad zinc scope. LME data come from Westmetall and FX data follow
the same maintained historical-plus-recent-close policy as copper.

## Underlying selection

The physical raw scope includes zinc-labelled observations across forms, grades, producers, and
symbols. Zinc dust dominates parts of the broad market but is not economically comparable with a
zinc-ingot certificate and is excluded from the underlying basket.

The approved basket contains ingot grades 99.97 and 99.98. Eligible rows require:

- an exact target ingot grade;
- cash or cash-matching contract;
- positive executed price and quantity.

The daily basket price is volume weighted across all eligible rows. Output preserves total
quantity, grade-specific quantities, and a composition label identifying 99.97-only, 99.98-only,
or two-grade dates. Current coverage includes 239 two-grade dates, 158 dates with only 99.97, and
157 dates with only 99.98, for total volume of 155,602 tonnes.

`build_physical_benchmark.py` produces `zinc_9798_cash_daily.csv`.

## Intrinsic proxy and alignment

The intrinsic proxy is

`LME cash zinc USD/kg × free-market USD/IRR`.

USD/IRR is a workspace input owned by `shared/market_data/fx.py` and stored only at
`shared/data/raw/fx/usd_to_rial.csv`. Zinc reads it directly; there is no Zinc-local FX collector,
CSV, or snapshot archive.

LME and FX are joined as-of to the latest observation on or before each target date. Source dates
and data ages are retained. Missing or stale observations are visible rather than silently treated
as exact-date inputs.

## Three valuation views

1. Physical versus intrinsic:
   `100 × (physical basket / intrinsic proxy - 1)`.
2. Certificate versus intrinsic:
   `100 × (certificate settlement / intrinsic proxy - 1)`.
3. Primary certificate versus estimated domestic physical value:
   interpolate the observed physical/intrinsic ratio between exact physical/certificate anchors,
   reconstruct physical value, and calculate the certificate premium or discount.

The primary method does not extrapolate outside the first and last observed anchors. The processed
outputs are `data/processed/bubble/physical_vs_intrinsic_bubble.csv`,
`data/processed/bubble/certificate_vs_intrinsic_bubble.csv`, and
`data/processed/bubble/zinc_certificate_bubble.csv`. The physical benchmark is separately stored
at `data/processed/physical/zinc_9798_cash_daily.csv`; none of the bubble files is a canonical
store for certificate or physical records.

## Regression sensitivity

The regression workflow predicts physical price from the intrinsic proxy and selects a predefined
specification using time-series cross-validation. It is a robustness check only. Certificate price
is not a feature, and the approved ratio-interpolation output remains the main result.

## Notebooks and report

Both active notebooks include the shared read-only dashboard for source coverage, separate
physical/certificate activity and prices, physical goods counts, and existing validated bubble
series. Zinc-specific grade and benchmark assumptions remain local.

- `01_zinc_analysis.ipynb`: source audit, grade coverage, supplier concentration, unit checks,
  basket construction, and activity visualization.
- `02_bubble_analysis.ipynb`: three bubble definitions, anchor interpolation, and regression
  sensitivity.
- `reports/zinc/research/zinc_research_report.tex`: English research report with reproducible
  figures.

## Reproduction

From the repository root, run collectors first and then builders in dependency order:

```powershell
python .\commodity\zinc\src\zinc\collectors\lme.py
python .\shared\market_data\fx.py
python .\commodity\zinc\src\zinc\collectors\certificate.py
python .\commodity\zinc\src\zinc\collectors\physical.py
python .\commodity\zinc\src\zinc\processing\build_physical_benchmark.py
python .\commodity\zinc\src\zinc\processing\build_intrinsic_bubbles.py
python .\commodity\zinc\src\zinc\processing\build_certificate_bubble.py
python .\commodity\zinc\src\zinc\processing\build_intrinsic_regression.py
```

## Validation and limitations

- Source identities, dates, units, and schemas are validated before merge.
- Grade shares and daily quantities remain auditable.
- Final prices use IRR/kg.
- Exact anchors are distinguished from interpolated observations.
- Raw zinc dust is never reclassified as ingot.

The intrinsic proxy is a transparent external factor, not a complete domestic parity model. Basket
composition and sparse physical anchors should be considered when interpreting certificate bubbles.
