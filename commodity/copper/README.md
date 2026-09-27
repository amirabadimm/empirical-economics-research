# Copper Certificate Valuation

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

## Shared execution checkpoint (2026-09-22)

The delivered comparison uses the shared engine in `shared/certificate_pipeline`.
Project-specific collectors, builders, and comparison sources are registered in `pipeline.json`.
Run `python refresh_powerbi.py` to rebuild from local sources, add `--collect` to fetch
new available source data first, or add `--plan` to preview the steps without writing.
The existing double-click launcher retains its local-rebuild behavior.
The engine stops on a failed step and publishes the delivery CSV only after all builders succeed.
Product eligibility, alignment methods, and economic interpretation remain product-specific.
Completed software delivery does not itself resolve the economic assumptions documented below.

Double-click `refresh_powerbi.cmd` in this project to rebuild its physical benchmark, comparison, and `outputs/power_bi/copper_certificate_physical_comparison.csv` for Power BI from existing raw inputs.

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
