# Copper Warehouse-Receipt Certificate: Research Workflow

## Full copper refresh (2026-09-27)

Completed the online production refresh with `refresh_powerbi.py --collect`,
then rebuilt intrinsic regression, forward-gap analysis, presentation timelines
and report figures. Cancelled global research collectors remain removed.

- LME: 4,738 rows through 2026-09-25.
- Shared USD/IRR: 13,103 rows through 1405/07/04 (2026-09-26).
- Certificate raw: 293 rows through 2026-09-26; 214 positive-volume observations.
- Physical raw: 1,175 rows; eligible daily benchmark: 799 rows through
  1405/06/29 (2026-09-20). No newer eligible physical trade was returned.
- Production comparisons: 206 primary, 799 physical/intrinsic and 214
  certificate/intrinsic rows; distribution: 1,219 rows; Power BI: 206 rows.
- Primary bubble remains bounded through 2026-09-20; no extrapolation added.
- Regression: 214 rows and 36 anchors; forward-gap diagnostic: 16 trade dates;
  presentation timeline: 342 daily rows and 250 events, with 36 overlaps.
- Validation: all 17 copper and shared certificate-pipeline tests passed.

This checkpoint supersedes earlier coverage and row counts below.

## Cancelled global research collectors (2026-09-27)

The global copper / COCHILCO research project is cancelled. Its eight collectors
and their dedicated tests have been removed; there is no ongoing collection or
resumption plan. Existing raw data and source snapshots remain frozen under the
workspace preservation rules. Historical research documents are archival only.
The active copper product uses physical, certificate and LME collectors plus shared FX.
Run `python commodity/copper/refresh_powerbi.py --collect` from the workspace root
to update those sources and rebuild the production outputs.

## Source refresh checkpoint (2026-09-26)

Online FX, Westmetall/LME, IME certificate and physical collectors completed.
LME coverage ends 2026-09-25; shared FX ends 2026-09-24 (1405/07/02).
Certificate raw coverage ends 2026-09-24, but the latest positive-volume
certificate comparison is 2026-09-23 (213 observations). Eligible physical
benchmark and bounded primary bubble end 2026-09-20 (206 primary observations).
No extrapolation was added. All three production comparisons, both percentile
methods, Power BI delivery and report figures were rebuilt. Research-only
regression, historical gap studies and timelines were not refreshed.

## Distribution update (2026-09-26)

The distribution CSV now contains signed bubbles and two chronological expanding
percentiles: `expanding_percentile` (equal observation weights) and
`recent_weighted_percentile` (exponential calendar-day weights, 90-day half-life).
The builder's `HALF_LIFE_DAYS` is configurable. Each date includes itself and ties
using <=; the first observation ranks at 100. History count and effective weighted
count expose small-sample limitations. Values are not smoothed or made absolute.
Standalone CDF and absolute-exceedance plots/columns are replaced for this project;
other commodities retain their existing behavior. Rebuild the distribution before
running the updated notebook cells. The histogram is full-sample; percentile ranks
use only rows through each date. Interpolated source values can still use later
anchors, so these are not vintage-safe backtest signals. Primary and both intrinsic
comparisons remain separate. Canonical bubble calculations are unchanged.

## Production consolidation (2026-09-26)

The production refresh now calls `build_valuation.py`, preparing all copper inputs
once through `valuation_inputs.py` for the three approved comparisons. Individual
builders remain usable. CSV names, economic formulas and coverage rules are unchanged.
Power BI now copies canonical copper bubble values, with an independent consistency
check rather than publishing a separately calculated percentage.
See [output ownership](OUTPUTS.md) (in `docs/OUTPUTS.md` from the project root) for
routine versus research outputs. The English report now leads with the primary
comparison and uses data-driven figures instead of fixed numerical claims.

## Valuation presentation (2026-09-23)

The valuation notebook opens with the approved certificate-to-physical bubble.
Certificate-to-intrinsic and physical-to-intrinsic comparisons each have a separate
supporting chart. Intrinsic value is LME cash USD/kg multiplied by USD/IRR.
Shared dashboards explicitly select these three approved outputs, primary first;
experimental regression files are not mixed into the headline chart.
Historical investigations remain in a labeled research appendix. No valuation
formula, source data, or project completion status changed in this presentation update.

## Shared execution checkpoint (2026-09-22)

The delivered comparison uses the shared engine in `shared/certificate_pipeline`.
Project-specific collectors, builders, and comparison sources are registered in `pipeline.json`.
Run `python refresh_powerbi.py` to rebuild from local sources, add `--collect` to fetch
new available source data first, or add `--plan` to preview the steps without writing.
The existing double-click launcher retains its local-rebuild behavior.
The engine stops on a failed step and publishes the delivery CSV only after all builders succeed.
Product eligibility, alignment methods, and economic interpretation remain product-specific.
Completed software delivery does not itself resolve the economic assumptions documented below.

The refresh also runs `build_bubble_distribution.py`. It maps each explicit copper bubble series
to the shared schema, writes `data/processed/bubble/copper_bubble_distribution.csv` atomically, and saves
three-panel distribution, empirical-CDF, and absolute-exceedance plots under
`data/processed/analysis`. Certificate/physical distributions include observed anchors and
bounded linear interpolations, flagged by `point_method` and `is_interpolated`. The table has
1,215 rows across certificate/physical,
certificate/intrinsic, and physical/intrinsic types at the 2026-09-21 checkpoint.
Active notebooks render the same three measures as clean, interactive Plotly panels.

Power BI reads this project's `outputs/power_bi/copper_certificate_physical_comparison.csv`. Double-click `refresh_powerbi.cmd` to rebuild the physical benchmark, analytical comparison, and presentation CSV from existing raw inputs. The export retains observed versus interpolated physical-price methods. Run the collectors first when new source data is needed.

Last reviewed: 2026-09-19

## Research objective

The project estimates the premium or discount of the Iranian copper-cathode warehouse receipt
relative to a comparable domestic physical-market benchmark. LME cash copper and the free-market
USD/IRR rate provide an external intrinsic-price proxy and support basis diagnostics. The primary
valuation remains anchored to observed domestic physical trades.

## Data checkpoint

| Source | Coverage |
|---|---|
| LME cash copper | 4,733 observations through 2026-09-18 |
| Free-market USD/IRR | 13,096 observations through 1405/06/26 |
| Certificate | 288 calendar rows; 210 positive-trading days through 2026-09-20 |
| Broad physical copper cathode | 1,175 rows through 1405/06/29 |
| Approved NCI cash benchmark | 799 trading days through 1405/06/29 |

The primary certificate output contains 206 dates from 2025-10-26 through 2026-09-20: 36 observed
physical anchors and 170 interpolated observations. Its mean estimated premium is 5.72% and its
median is 7.10%. No extrapolation is applied after the last supported anchor.

## Repository architecture

- `data/raw`: canonical source files and immutable snapshots; never written by analysis.
- `data/interim`: reproducible intermediate data.
- `data/processed/physical`: physical benchmarks and physical-only diagnostics.
- `data/processed/certificate`: certificate-only derived tables, if introduced.
- `data/processed/bubble`: bubble, intrinsic-comparison, and model outputs.
- `data/processed/analysis`: other presentation or analytical tables.
- `src/copper/collectors`: explicit commodity-specific source wrappers.
- `src/copper/processing`: deterministic benchmark and valuation builders.
- `notebooks`: executed analysis and saved figures.
- `outputs` and `reports`: local presentation and research deliverables.
- `shared/ime_data`: reusable Iran Mercantile Exchange collection logic.

Raw data, source snapshots, credentials, logs, caches, and bulk outputs are excluded from Git.

## Sources and collectors

### LME cash copper

`collectors/lme.py` delegates annual Westmetall collection from 2008 onward to the shared
`shared/market_data/lme.py` engine; Copper keeps only its explicit field, filename, and wrapper.
The engine archives source HTML, preserves missing markers, refreshes recent periods, validates
date uniqueness, and writes atomically. The analytical field is cash settlement in USD/tonne.

The physical collector archives new complete IME responses once in
`shared/data/raw/ime/physical`; project-local physical snapshots are frozen legacy rebuild inputs.

### Free-market USD/IRR

`shared/market_data/fx.py` owns the workspace canonical series at
`shared/data/raw/fx/usd_to_rial.csv`, merging maintained history with TGJU close observations.
Copper reads that file directly and keeps no project-local FX copy.
Historical user-supplied rows are preserved. The canonical unit is IRR per USD, and source labels
remain explicit so legacy midpoint and recent close observations are distinguishable.

### Warehouse-receipt certificate

`collectors/certificate.py` uses the shared CDC collector with copper-specific identity checks.
`TodaySettlementPrice` is the analytical certificate price. `TradesValue / TradesVolume` is a
rounding-tolerant consistency check, not a replacement price. Zero-volume dates remain in raw data
but are excluded from price analysis.

### Physical market

`collectors/physical.py` downloads and archives monthly official IME physical-market responses
before filtering. The canonical raw file is refreshed incrementally, idempotently, and atomically.
The collector retains the broad copper-cathode source scope; benchmark eligibility is enforced by
the processing layer.

## Comparable physical benchmark

The approved underlying includes National Iranian Copper Industries Company cathode under the
historical symbols `NCI-CCAA-00` and `NCI-OACCAA-00`. Eligible rows must satisfy all of the
following:

- exact approved cathode identity;
- cash or cash-matching contract;
- positive executed price and quantity;
- no forward, credit, other producer, or “copper cathode 2” observation.

The daily benchmark price is volume weighted. Cash and cash-matching quantities remain separate
for audit even when their prices coincide. If eligible contract methods produce different prices
on the same date, the builder stops rather than silently selecting one.

Daily cash, matching, and total transaction values are retained in IRR. They are converted from
the IME `TotalPrice` source field (reported in million IRR), with a rounding-tolerant check against
`Price × Quantity`. `physical_trades_value_irr` is also propagated to the physical-versus-intrinsic
analysis; certificate transaction value remains the source `TradesValue` in IRR.

`build_physical_benchmark.py` produces `data/processed/physical/nci_copper_cash_daily.csv`.

## Market alignment and intrinsic proxy

The external intrinsic proxy is

`LME cash USD/kg × free-market USD/IRR`.

LME and FX are joined as-of to the latest observation on or before each target date. Source dates
and data ages remain in every output. This accommodates different trading calendars without
pretending that a stale observation is contemporaneous.

## Valuation outputs

### Physical versus intrinsic

`physical_vs_intrinsic_bubble.csv` reports

`100 × (observed physical price / intrinsic proxy - 1)`.

### Certificate versus intrinsic

`certificate_vs_intrinsic_bubble.csv` reports

`100 × (certificate settlement / intrinsic proxy - 1)`.

### Primary certificate valuation

The primary method estimates the domestic physical price on certificate dates. At each exact
physical/certificate anchor, it calculates

`physical ratio = observed physical price / intrinsic proxy`.

The ratio is linearly interpolated between adjacent anchors and multiplied by the date-specific
intrinsic proxy. No extrapolation is allowed before the first anchor or after the last. The final
bubble is

`100 × (certificate settlement / estimated physical price - 1)`.

`build_certificate_bubble.py` produces
`data/processed/bubble/copper_certificate_bubble.csv`. All direct intrinsic bubbles and
regression outputs are also stored under `data/processed/bubble`; they do not serve as canonical
certificate or physical record stores.

## Regression sensitivity

The regression workflow is an experimental sensitivity check, not the primary model. It predicts
physical price from the intrinsic proxy and chooses among predefined specifications using
time-series cross-validation and out-of-sample RMSE. Current model selection is documented in the
processed output and notebook. Certificate price is never used as a feature.

## Forward trades inside the 102-day cash gap

The exact NCI cash series has a 102-day gap between 1404/09/26 and 1405/01/09. This is a cash
benchmark gap, not a market closure. `build_forward_gap_analysis.py` isolates exact-symbol forward
and forward-matching trades strictly inside the interval.

The diagnostic contains 16 trade dates and 26,420 tonnes. Each forward weighted price is compared
with the previous cash anchor, the next cash anchor, and a linear bridge between them. Forward
prices range from 7.16% to 33.73% above the previous cash anchor and from 14.05% below to 7.26%
above the next cash anchor. These observations are not inserted into the cash benchmark because
maturity and financing adjustments have not been established.

## Notebooks and presentation outputs

Both active notebooks use Plotly for their analytical figures and include the shared read-only dashboard for source coverage, separate
physical/certificate activity and prices, physical goods counts, and existing validated bubble
series. Copper-specific LME and valuation analysis remains local.

- `01_lme_analysis.ipynb`: LME and market-input diagnostics.
- `02_certificate_analysis.ipynb`: certificate valuation, regression sensitivities, forward-gap
  analysis, certificate volume, and the exact observed-anchor bubbles.
- `build_presentation_timeline.py`: presentation-ready daily and event timelines.

Notebooks read raw and processed data but never modify canonical raw files.

## Reproduction

From the repository root:

```powershell
python .\commodity\copper\src\copper\collectors\lme.py
python .\shared\market_data\fx.py
python .\commodity\copper\src\copper\collectors\certificate.py
python .\commodity\copper\src\copper\collectors\physical.py
python .\commodity\copper\src\copper\processing\build_physical_benchmark.py
python .\commodity\copper\src\copper\processing\build_intrinsic_bubbles.py
python .\commodity\copper\src\copper\processing\build_certificate_bubble.py
python .\commodity\copper\src\copper\processing\build_intrinsic_regression.py
python .\commodity\copper\src\copper\processing\build_presentation_timeline.py
python .\commodity\copper\src\copper\processing\build_forward_gap_analysis.py
```

## Validation and interpretation

- Dates must be unique and sorted in canonical daily outputs.
- Price and volume must be positive in analytical samples.
- All final prices use IRR/kg.
- As-of source dates and ages must remain auditable.
- Interpolation is restricted to the observed anchor range.
- Model sensitivities must remain clearly separated from the approved primary method.

Results are research documentation, not investment advice. The limited and uneven physical-anchor
sample is the principal constraint on structural interpretation.
