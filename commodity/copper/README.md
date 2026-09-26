# Copper Certificate Valuation

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
See [output ownership](docs/OUTPUTS.md) for
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

Double-click `refresh_powerbi.cmd` in this project to rebuild its physical benchmark, comparison, and `outputs/power_bi/copper_certificate_physical_comparison.csv` for Power BI from existing raw inputs.

This commodity workspace now contains two governed research systems: the original Iranian
certificate-valuation study and a separate global copper-market data foundation. The latter
reuses the existing LME history and never reacquires it.

## Global copper-market data foundation

Public first-wave sources are organized under `data/raw/global_market/<source>` with immutable
source responses or files and atomic canonical manifests/tables. As of 2026-09-02 the collected
foundation contains BGS world copper statistics (13,836 rows), main-contract COMEX copper CFTC
positioning (869 weekly rows with a complete canonical report date from 2010-01-05 through
2026-08-25), IRENA world power capacity (543 rows), NBS China copper-products
output (44 rows), 206 USGS monthly copper survey workbooks, and COCHILCO company-level Chilean
mine production (5,852 rows; continuous country totals from 2006-01 through 2026-05). CME now
includes 76 preserved official Copper Stocks workbooks (2,065 warehouse/status rows covering 76
activity dates from 2012-05-09 through 2026-08-31) and 131 preserved official metals bulletins
(124 unique HG futures activity dates from 2014-06-27 through 2026-08-28, with Globex,
open-outcry, and PNT/PIT activity). The same bulletins now provide 3,294 contract-date HG price
rows with contract month, Globex open/high/low, official settlement and change, volume by channel,
and open interest. Bulletin dates are archive-spaced rather than a continuous trading calendar. The
SHFE foundation now contains 54,426 official copper contract-date observations across 4,536
trading dates from 2008-01-02 through 2026-09-02, plus daily copper warrants for 2,992 dates
from 2014-05-19 through 2026-09-02 and weekly inventory/capacity for 594 dates from 2014-05-23
through 2026-08-28. Warrants and weekly physical inventory remain separate measures. The
unauthenticated UN Comtrade preview returned 781 China copper-trade aggregates for a
non-continuous 2010-2024 sample; it is retained with an explicit incomplete-preview flag and is
not promoted as full history. Exact licensed PRA benchmarks
(Yangshan/US/Europe premiums and spot TC/RC) remain entitlement-gated and are not replaced with
fabricated free series.

The professional indicator/source registry is `docs/first_wave_source_dictionary.csv`; source
assurance and collection constraints are documented in `docs/FIRST_WAVE_SOURCE_ASSURANCE.md`.

## Research question

Does the Iranian copper-cathode warehouse receipt trade at a premium or discount to a
comparable domestic physical-market price, after accounting for movements in LME cash copper
and the free-market USD/IRR exchange rate?

## Current checkpoint

- Data checkpoint: 2026-09-19
- Certificate: 288 calendar observations, 210 positive-trading days, through 2026-09-20
- Canonical physical market: 1,175 rows through 1405/06/29
- LME cash copper: 4,733 observations through 2026-09-18
- Free-market USD/IRR: 13,096 observations through 1405/06/26
- Processed physical benchmark and forward-gap diagnostic: `data/processed/physical`
- Bubble and regression outputs: `data/processed/bubble`
- Presentation timelines: `data/processed/analysis`

Both active copper notebooks use interactive Plotly figures. Notebook calculations remain
read-only with respect to canonical source files; saved outputs are cleared before versioning.

## Comparable physical underlying

The approved domestic benchmark includes only National Iranian Copper Industries Company
cathode under the historical symbols `NCI-CCAA-00` and `NCI-OACCAA-00`, using cash and
cash-matching contracts with positive executed price and quantity. Forward, credit, other
producers, and “copper cathode 2” are excluded from the comparable scope.

The daily physical price is volume weighted. The primary certificate valuation interpolates
the ratio of domestic physical price to LME–FX intrinsic price between exact physical/certificate
anchors. No extrapolation is allowed outside the observed anchor range. A time-series regression
using intrinsic price as its sole feature is retained as an experimental sensitivity check.

The separate `nci_copper_forward_gap.csv` diagnostic preserves the cash-only benchmark scope.
It covers 16 forward-trade dates and 26,420 tonnes strictly inside the 102-day cash gap,
comparing each forward weighted price with both cash anchors and a linear bridge.

## Main current result

The primary output contains 206 certificate-trading days from 2025-10-26 to 2026-09-20:
36 observed physical anchors and 170 interpolated days. The estimated certificate premium to
domestic physical value averages 5.73%, with a median of 7.16%. Interpretation is limited by
the small and temporally uneven physical anchor sample.

## Reproduction from the repository root

```powershell
python .\commodity\copper\src\copper\collectors\lme.py
python .\shared\market_data\fx.py
python .\commodity\copper\src\copper\collectors\certificate.py
python .\commodity\copper\src\copper\collectors\physical.py
python .\commodity\copper\src\copper\collectors\global_market.py --sources nbs irena bgs cftc
python .\commodity\copper\src\copper\collectors\usgs_archive.py
python .\commodity\copper\src\copper\collectors\cochilco.py --report-year 2026 --report-month 6 --backfill
python .\commodity\copper\src\copper\collectors\comtrade.py
python .\commodity\copper\src\copper\collectors\cme.py
python .\commodity\copper\src\copper\collectors\cme_bulletins.py
python .\commodity\copper\src\copper\collectors\shfe.py
python .\commodity\copper\src\copper\collectors\shfe_inventory.py
python .\commodity\copper\src\copper\processing\build_physical_benchmark.py
python .\commodity\copper\src\copper\processing\build_intrinsic_bubbles.py
python .\commodity\copper\src\copper\processing\build_certificate_bubble.py
python .\commodity\copper\src\copper\processing\build_intrinsic_regression.py
python .\commodity\copper\src\copper\processing\build_presentation_timeline.py
python .\commodity\copper\src\copper\processing\build_forward_gap_analysis.py
```

The full methodology, source contracts, validations, and limitations are documented in
[`docs/WORKFLOW.md`](docs/WORKFLOW.md). The English research report is in
[`reports/copper/research`](../../reports/copper/research/).
# Historical bubble distributions

`data/processed/bubble/copper_bubble_distribution.csv` is the standardized Power BI table for all
computed copper bubble types. Certificate-versus-physical rows include observed physical anchors
and bounded linear interpolations. `point_method` and `is_interpolated` identify every row. The table contains signed bubble percentages,
empirical `F(x)`, and `P(|Bubble| >= |x|)`. Distribution figures are written to
`data/processed/analysis`.
