# Copper Project Status

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

As of 2026-09-21, the standardized bubble-distribution output contains 1,215 observations:
206 certificate-versus-physical (36 observed and 170 interpolated), 210 certificate-versus-intrinsic, and 799
physical-versus-intrinsic. Matching figures and notebook cells are available.

The project-local Power BI certificate/physical CSV has 201 rows at this checkpoint.

Last updated: 2026-09-19

## Global copper-market collection checkpoint

The global-market subsystem has been added without modifying the existing LME raw history.
Completed public collections are: BGS world copper statistics (13,836 observations, 1970 onward
depending on table), CFTC main COMEX Grade #1 disaggregated futures-only positioning (869 weekly
observations from 2010-01-05 through 2026-08-25), IRENA world generating capacity by technology/grid status (543
observations, 2000-2025), NBS China copper-products output via DBnomics (44 current-vintage
observations), and 206 official USGS monthly Copper Mineral Industry Survey workbooks spanning
2005-2025 with source gaps as published.

The second collection pass added 5,852 COCHILCO company-level observations. Monthly Chilean
country totals are complete from 2006-01 through 2026-05 with 22 company/aggregate columns and
no duplicate keys. The public UN Comtrade preview was queried for every month from 2000-01
through 2026-08 for HS 2603, 7403, and 7404 imports and exports. It returned only 781 aggregate
rows across a non-continuous 2010-2024 sample, so this output is explicitly marked
`unauthenticated_preview_incomplete`; a free API subscription key is required before promotion
to a complete trade-history input.

The CME collection now bypasses the live-site WAF without substituting a third-party dataset:
the collectors use Internet Archive replay of official CME files and preserve every source file.
All 76 distinct Copper Stocks XLS workbooks parse to 2,065 canonical warehouse/status rows across
76 activity dates from 2012-05-09 through 2026-08-31. All 131 distinct metals-bulletin PDFs parse
to 124 unique HG futures trade dates from 2014-06-27 through 2026-08-28. The bulletin table retains
3,294 unique contract-date price rows across those dates, including Globex OHLC, official
settlement/change, volume channels, and open interest. Contract-level volume reconciles to each
published aggregate after including the four legacy open-outcry dates. The dates remain sparse.

The SHFE presentation-layer slider is also no longer a data block. Official dated Daily Express
JSON files produced 54,426 copper contract observations across 4,536 trading dates from
2008-01-02 through 2026-09-02, including OHLC, previous/current settlement, volume, open interest,
open-interest change, and turnover where published. Official Daily Warrant files produced three
tax-status totals for 2,992 dates from 2014-05-19 through 2026-09-02. Official Weekly Inventory
files produced the same three categories for 594 dates from 2014-05-23 through 2026-08-28,
retaining physical inventory, inventory change, warrants, warrant change, and warehouse capacity.
The collector handles SHFE's 2025-11-18 publication transition from all-product JSON files to
official product-specific HTML files. Daily and weekly totals reconcile exactly across that break.

FRED is registered but its server repeatedly reset connections during this collection session;
no partial canonical FRED file was written. IEA Global EV Outlook 2026 is free but its XLSX
download currently requires an IEA account session. Licensed physical-premium and spot TC/RC
series remain explicit entitlement inputs, not reconstructed substitutes.

The live CME host still returns an IP/WAF denial, but its stock and bulletin datasets are now
collected through preserved official files. CME's official `/ftp/daily_volume/` index exposes
dated workbooks from 2014 onward, but scripted workbook retrieval from the current environment
returns CME's explicit automated-access prohibition; the index is therefore discovered but not
misrepresented as collected. SHFE's report pages still show an interactive slider,
but dated official JSON data files are directly collectible. BLS's public API and bulk host remain
blocked from the current network.

The Census private-construction workbooks and exact data-center definition are confirmed, with
the named monthly series beginning in 2014. Census blocks the workbook download from the current
network and now requires an API key for Economic Indicators queries, so no partial or third-party
substitute was accepted.

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
