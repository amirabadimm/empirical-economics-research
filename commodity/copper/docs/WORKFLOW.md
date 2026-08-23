# Copper Warehouse-Receipt Certificate: Research Workflow

Last reviewed: 2026-08-23

## Research objective

The project estimates the premium or discount of the Iranian copper-cathode warehouse receipt
relative to a comparable domestic physical-market benchmark. LME cash copper and the free-market
USD/IRR rate provide an external intrinsic-price proxy and support basis diagnostics. The primary
valuation remains anchored to observed domestic physical trades.

## Data checkpoint

| Source | Coverage |
|---|---|
| LME cash copper | 4,714 observations through 2026-08-21 |
| Free-market USD/IRR | 13,074 observations through 1405/05/31 |
| Certificate | 263 calendar rows; 190 positive-trading days through 2026-08-22 |
| Broad physical copper cathode | 1,170 rows through 1405/06/01 |
| Approved NCI cash benchmark | 794 trading days through 2026-08-23 |

The primary certificate output contains 183 dates from 2025-10-26 through 2026-08-17: 30 exact
physical anchors and 153 interpolated observations. Its mean estimated premium is 5.57% and its
median is 6.96%.

## Repository architecture

- `data/raw`: canonical source files and immutable snapshots; never written by analysis.
- `data/interim`: reproducible intermediate data.
- `data/processed`: derived analytical outputs.
- `src/copper/collectors`: explicit commodity-specific source wrappers.
- `src/copper/processing`: deterministic benchmark and valuation builders.
- `notebooks`: executed analysis and saved figures.
- `outputs` and `reports`: local presentation and research deliverables.
- `shared/ime_data`: reusable Iran Mercantile Exchange collection logic.

Raw data, source snapshots, credentials, logs, caches, and bulk outputs are excluded from Git.

## Sources and collectors

### LME cash copper

`collectors/lme.py` retrieves annual Westmetall tables from 2008 onward. It archives the source
HTML, preserves missing markers, refreshes only recent periods during incremental runs, validates
date uniqueness, and writes atomically. The analytical field is cash settlement in USD/tonne.

### Free-market USD/IRR

`collectors/fx.py` merges the maintained historical series with recent TGJU close observations.
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

`build_physical_benchmark.py` produces `nci_copper_cash_daily.csv`.

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

`build_certificate_bubble.py` produces `copper_certificate_bubble.csv`.

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

- `01_lme_analysis.ipynb`: LME and market-input diagnostics.
- `02_certificate_analysis.ipynb`: certificate valuation, regression sensitivities, forward-gap
  analysis, certificate volume, and the exact observed-anchor bubbles.
- `build_presentation_timeline.py`: presentation-ready daily and event timelines.

Notebooks read raw and processed data but never modify canonical raw files.

## Reproduction

From the repository root:

```powershell
python .\commodity\copper\src\copper\collectors\lme.py
python .\commodity\copper\src\copper\collectors\fx.py
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
