# Copper Project Status

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

As of 2026-09-21, the standardized bubble-distribution output contains 1,215 observations:
206 certificate-versus-physical (36 observed and 170 interpolated), 210 certificate-versus-intrinsic, and 799
physical-versus-intrinsic. Matching figures and notebook cells are available.

The project-local Power BI certificate/physical CSV has 201 rows at this checkpoint.

Last updated: 2026-09-22

Both active notebooks now include the governed workspace dashboard for source coverage,
physical/certificate activity, goods composition, prices, and validated bubble visualization.

The market-input collectors and all dependent valuation outputs have been refreshed. Processed
physical outputs now live under `data/processed/physical`, bubble/model outputs under
`data/processed/bubble`, and presentation tables under `data/processed/analysis`. Current
coverage is LME through 2026-09-18, shared free-market USD/IRR through 1405/06/26, certificate data
through 2026-09-20, and the approved NCI cash benchmark through 1405/06/29.

The primary certificate bubble contains 206 observations from 2025-10-26 through 2026-09-20,
including 36 observed physical anchors and 170 interpolated dates. Its mean premium is 5.72% and
its median is 7.10%. Certificate transaction value is present as `certificate_trades_value_irr`;
physical transaction value is now present as `physical_trades_value_irr` in the daily benchmark
and physical-versus-intrinsic output.

The 2026-09-21 incremental refresh reached 288 certificate rows (210 traded days), 1,175
canonical physical rows, 4,733 LME observations, and 13,096 shared FX observations. Rebuilt
physical, intrinsic, primary bubble, regression, presentation, and forward-gap outputs; the
primary bubble is bounded by observed physical anchors. Twenty copper tests passed and all 27
code cells in the certificate analysis notebook executed in memory.

On 2026-09-19, both active copper notebooks were converted from Matplotlib/Seaborn plots to
interactive Plotly figures. The LME and certificate notebooks executed all 17 and 27 code cells,
respectively; saved notebook outputs remain cleared.
