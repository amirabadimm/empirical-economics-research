# Zinc Research Status

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

## Valuation presentation (2026-09-23)

The valuation notebook opens with the approved certificate-to-physical bubble.
Certificate-to-intrinsic and physical-to-intrinsic comparisons each have a separate
supporting chart. Intrinsic value is LME cash USD/kg multiplied by USD/IRR.
Shared dashboards explicitly select these three approved outputs, primary first;
experimental regression files are not mixed into the headline chart.
Historical investigations remain in a labeled research appendix. No valuation
formula, source data, or project completion status changed in this presentation update.

The project-local Power BI certificate/physical CSV has 201 rows at this checkpoint.

Last updated: 2026-09-19
Stage: approved 99.97/99.98 physical basket with bounded certificate valuation

The official incremental refresh reached 288 certificate rows through 2026-09-20 (210 traded
days), 6,398 broad physical rows through 1405/06/25 (3,581 positive trades), 4,733 LME dates
through 2026-09-18, and 13,096 shared USD/IRR dates through 1405/06/26.

The rebuilt physical benchmark has 563 days through 1405/06/29. The primary certificate bubble
has 206 dates through 2026-09-20: 50 observed physical anchors and 156 bounded interpolations.
Its mean premium is 0.80%; the direct certificate/intrinsic mean is -20.54% across 208 dates.
No extrapolation is used in the primary bubble.

Both zinc notebooks use Plotly and executed against current data. The static research report
retains its earlier checkpoint. Continue monitoring input freshness and physical basket
composition before interpreting the modeled premium.
# Bubble distribution status

As of 2026-09-21, the standardized output contains 979 observations: 206
certificate-versus-physical (50 observed and 156 interpolated), 210 certificate-versus-intrinsic, and 563
physical-versus-intrinsic. Matching figures and notebook cells are available.
