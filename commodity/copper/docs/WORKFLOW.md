# Copper Warehouse-Receipt Certificate: Research Workflow

Last reviewed: 2026-08-29

## Research objective

The project estimates the premium or discount of the Iranian copper-cathode warehouse receipt
relative to a comparable domestic physical-market benchmark. LME cash copper and the free-market
USD/IRR rate provide an external intrinsic-price proxy and support basis diagnostics. The primary
valuation remains anchored to observed domestic physical trades.

## Data checkpoint

| Source | Coverage |
|---|---|
| LME cash copper | 4,719 observations through 2026-08-28 |
| Free-market USD/IRR | 13,079 observations through 1405/06/05 |
| Certificate | 268 calendar rows; 194 positive-trading days through 2026-08-27 |
| Broad physical copper cathode | 1,171 rows through 1405/06/02 |
| Approved NCI cash benchmark | 795 trading days through 2026-08-24 |

The primary certificate output contains 188 dates from 2025-10-26 through 2026-08-24: 32 exact
physical anchors and 156 interpolated observations. Its mean estimated premium is 5.64% and its
median is 7.17%.

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

Both active notebooks include the shared read-only dashboard for source coverage, separate
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

## Global copper-market raw workflow

`collectors/global_market.py` collects official/public structured sources into isolated source
families beneath `data/raw/global_market`: BGS copper statistics, CFTC COMEX Grade #1 positioning,
IRENA power capacity, NBS copper-products output, and registered FRED controls. Responses are
archived before canonical CSVs are atomically replaced. BGS is fully paginated; CFTC archives are
read year-by-year and filtered to contract code `085692`; LME is deliberately excluded.

`collectors/usgs_archive.py` discovers both the official legacy index and current USGS copper
page, downloads each XLS/XLSX only once, validates the workbook signature, and records byte size
and SHA-256 in `usgs_copper_mis_manifest.csv`. Extraction from changing workbook layouts belongs
in an interim processing step; raw workbooks are never edited.

Source definitions, exact/proxy distinctions, access class, methodology breaks, and collection
routes are governed by `first_wave_source_dictionary.csv`. A failed source must not replace an
existing canonical file with empty or partial output.

`collectors/cochilco.py --backfill` uses five pinned January bulletin vintages plus the latest
bulletin to construct a continuous company-level monthly panel. It parses Spanish-formatted kMT
copper-content values, rejects vector/header mismatches, retains annual and monthly frequencies
separately, and resolves overlaps in favor of the latest publication vintage.

`collectors/comtrade.py` archives one official preview response per requested month for China's
world-partner imports and exports of HS 2603, 7403, and 7404. The unauthenticated preview endpoint
is demonstrably incomplete and must retain `source_access_tier=unauthenticated_preview_incomplete`.
It cannot be used as continuous trade history until rerun through the free authenticated API.

`collectors/cme.py` queries the Internet Archive CDX index for distinct captures of CME's official
`Copper_Stocks.xls`, preserves every immutable workbook, parses warehouse-level registered,
eligible, and total short tons, and selects the latest capture for each activity date. Older
workbooks that publish only the exchange total remain valid rather than receiving invented status
detail. `collectors/cme_bulletins.py` similarly preserves distinct official Section 62 metals
bulletins and extracts only the unambiguous HG aggregate row. It retains Globex, legacy
open-outcry, and PNT/PIT volume separately, derives their sum, and records open interest and its
published change. Every output row carries its archive capture and replay URL; manifests expose
the original CME URL and any parse error. Contract-month settlements remain raw-PDF evidence
until a geometry-aware parser is separately validated.

`collectors/shfe.py` incrementally checks official dated Daily Express JSON files, archives each
published trading-day response once, normalizes legacy fixed-width identifiers, and filters only
the exchange's `cu_f` futures contracts. The canonical table preserves each expiry rather than
inventing a continuous contract. Prices remain CNY per metric tonne; volume and open interest
remain SHFE lots; turnover is retained in the source's 10,000-CNY convention. Missing OHLC on an
untraded expiry is valid, while settlement, volume, and open interest are required.

`collectors/shfe_inventory.py` separately archives Daily Warrant and Weekly Inventory JSON files.
It preserves Total, Total (Tax included), and Total (Bonded) rows. Daily warrant tonnes must not
be relabelled as weekly physical inventory; weekly reports additionally retain inventory,
inventory change, and warehouse capacity. The public dated endpoints currently end in November
2025, so later missing periods remain missing until the replacement official route is identified.
