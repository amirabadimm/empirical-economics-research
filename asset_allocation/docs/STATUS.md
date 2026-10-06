# Status

Updated: 2026-10-06

Report generation 2026-10-06: `reports/REIT_USD_LEAD_LAG_REPORT.html` and the Markdown companion were built from the existing four-fund processed outputs, without refreshing market sources. The report contains three interactive Plotly charts, cumulative and event tables, 15 reportable of 20 USD lag coefficients, and three reportable predictive regressions; Kakh is explicitly suppressed where coverage is insufficient. The market endpoint is Friday 2026-10-02, while housing ends at the observed 2026-09-22 month end. The HTML is a regenerable local artifact; the Markdown summary is versioned.

Documentation review 2026-10-06: project and workspace workflows were reconciled to the active four-fund run sequence. This documentation pass did not refresh source data or recompute derived tables; their coverage and validation dates are recorded separately below.

The active four-fund notebook now has 12 cells and four Plotly figures, adding a common-sample 0–4-week USD lag curve and a compact predictive-regression table in place of the earlier correlation heatmap. The new derived lag table has 20 fund/lag rows: 15 reportable for Arzesh Maskan, Danik, and Kelid, while Kakh has only 16 common weeks and all five estimates are suppressed. Three of four predictive models meet the 52-week minimum; Kakh has 18 complete rows and is blank. Regressions use cash-reinvested fund returns, USD lags one/two, own lag one, and TEDPIX lag one. HAC(4) joint USD p-values, Benjamini–Hochberg FDR p-values, and same-sample incremental in-sample R² are reported. The notebook was reexecuted successfully. The prior 10-cell/three-figure heatmap checkpoint below is superseded.

The compact active REIT notebook now includes Kakh alongside Kelid, Danik, and Arzesh Maskan. It has 10 cells and three Plotly figures, and was reexecuted successfully. The custom daily panel has 2,052 traded sessions; the two-year weekly cumulative panel has 630 asset/week rows across four funds, TEDPIX, and USD/IRR. Daily, weekly, and monthly REIT returns use the custom reinvested-value path. The new same-period correlation table has 64 four-fund/benchmark/frequency/window cells, 42 reportable under minimum paired counts of 12 weekly or 6 monthly; suppressed estimates are blank. One-month, lag, and regression figures were removed from the active notebook. Their older derived files remain historical, not active estimates. Kakh and Arzesh Maskan have no recorded cash events, so their displayed paths remain incomplete as total-return histories. Earlier three-fund counts and return methods below are superseded.

The active REIT notebook now uses a custom assembly-date reinvestment scenario for its three fund cumulative lines. Three user-supplied approved distributions (Danik 1,800 IRR; Kelid 907 and 864 IRR) yield 1,948 traded-session derived rows and three audited reinvestment events. Its two-year market panel now has 525 week/asset rows across those three funds, TEDPIX, and USD/IRR. The notebook was reexecuted. TSETMC adjusted fund prices are no longer used for those active cumulative lines. The earlier adjusted-price chart counts and descriptions below are historical checkpoints. Correlation/regression cells still use traded closes and await the user's planned methodological review; payout completeness and actual cash dates remain unresolved.

The Kilid housing source was refreshed on 2026-10-06 through its validated, incremental collector. The immutable new page snapshot adds complete month 1405/06 to the 37-row canonical raw CSV; incomplete 1405/07 is excluded. The four-asset derived panel now has 127 level months and 126 return months, ending 1405/06. The housing chart has 24 monthly observations through 2026-09-22 and +160.7% cumulative price appreciation from 2024-10-21. The latest housing monthly return is +4.76%. Both allocation and REIT notebooks were reexecuted. Prior 1405/05, five-month YTD, 113-aligned-month, and 23-point housing statements below are superseded where they describe the active outputs; underlying older source refresh dates remain historical.

## Real estate fund extension (2026-10-05)

Update 2026-10-06: The active, renamed `notebooks/iran_reits_cross_asset_analysis.ipynb` now displays only Arzesh Maskan, Kelid, and Danik. It adds Plotly same-period and one-prior-day/week/Jalali-month USD correlations for trailing 1, 3, 6, 12, 24, and 48 Jalali months. The new derived pair panel has 4,964 rows and the correlation table has 108 cells, of which 96 meet the three-pair/nonconstant rule; all six one-month monthly cells for each lag/fund remain undefined. The last complete weekly anchor is 2026-10-02 and the last complete monthly period is 1405/06. Existing eight-fund raw histories and older processed tables remain intact but are filtered by the notebook; prior eight-fund notebook counts below are superseded as descriptions of the active view. The three-fund lag analysis uses traded-price returns and does not resolve the dividend audit.

Eight current real estate funds were identified through TSETMC search and their daily price histories collected through 2026-10-04. TEDPIX was refreshed to 4,298 daily observations through the same date. The separate monthly comparison panel covers 1401/07–1405/07; 1405/07 is incomplete and excluded by the correlation notebook. Six funds have at least six overlapping complete monthly returns with TEDPIX; Kakh and Emarat Dey have four and two, respectively, so their correlations are not reported. Fund returns are closing-price changes, not audited total returns. That earlier four-asset endpoint was subsequently superseded by the 2026-10-06 Kilid refresh.

The trailing-window extension now computes 48 fund-window rows for 1, 3, 6, 12, 24, and 48 months ending 1405/06. The processed table includes overlap counts, Pearson correlations, and OLS beta, intercept, R², and p-value. Plotly tables, heatmaps, and a selectable fund/window regression scatterplot are in `notebooks/iran_reits_cross_asset_analysis.ipynb`. The one-month column is undefined by design; other cells need at least three valid pairs.

The same English-language notebook now includes weekly returns and trailing 1, 3, 6, 12, and 24-month Plotly views. Weekly processing uses only the last 24 Jalali months of daily source data plus a preceding-week buffer. The derived panel contains 945 week/asset rows and 40 fund/window estimates through the completed Friday of 2026-10-02; the week ending 2026-10-09 is still incomplete. Fund labels are English transliterations. Weekly returns and regressions remain closing-price based pending the distribution and corporate-action audit.

The appended USD/IRR section uses the shared canonical rial-per-dollar series refreshed through 2026-10-04. It has 102 valid weekly USD returns in the bounded panel through 2026-10-02 and 40 fund/window regression rows. The 24-month samples combine older legacy midpoint weeks and recent TGJU close weeks, with the cross-method return excluded and method counts exposed. This is a distinct fund-on-USD comparison; the earlier TEDPIX results are unchanged.

The final notebook section now uses exchange-adjusted fund prices after collecting and validating 3,418 adjusted daily observations across eight funds. Kelid, Danik, and Malek Atiyeh changed relative to the superseded unadjusted cumulative results; the other five did not. Its two-year panel has 105 Friday-ending weeks through 2026-10-02, ten assets, and 1,050 week/asset rows. TEDPIX, USD/IRR, and five funds start from 2024-10-04; Kakh, Emarat Dey, and Kashaneh begin later. The Plotly line bridges missing weeks visually, but the processed panel does not fill them. Fund-level payout and adjustment semantics remain unaudited, so the chart is labelled exchange-adjusted price performance rather than verified total return. Monthly and weekly regressions still use unadjusted fund closes. The chart also overlays 24 observed monthly Tehran housing points through 2026-09-22, held in a separate processed panel. Housing shows +160.7% price appreciation since 2024-10-21, entirely from the flagged chain-linked Kilid proxy; it excludes rent and ownership costs and is not extrapolated to October.

A new notebook Plotly panel compares traded and exchange-adjusted closes for Kelid, Arzesh Maskan, and Danik. Kelid and Danik differ; Arzesh Maskan is identical in this feed. Two annual payments are source-verified and entered: Kelid 907 IRR per unit, payment from 2025-10-27; Malek Atiyeh 1,283 IRR per unit, payment from 2026-06-07. Danik's reopening notice confirms a cash distribution, and Arzesh Maskan has a payment-schedule disclosure, but their exact amounts and dates remain unverified. The eight-fund reinvestment builder computes known-payment paths only; complete annual payout coverage and total return are unresolved. Adjustment equality cannot imply no payouts.
The historical audit now explicitly reaches each fund's first exchange price (2022 for Arzesh Maskan, 2023 for Danik and Amin Shahr, and later for the others). Pre-2025 and annual payout gaps by fund are recorded in `docs/REIT_DIVIDEND_AUDIT.md`; source coverage remains two verified payments, while the derived daily price panel covers 3,418 observations. This review did not refresh prices or confirm additional payments.

## Confirmed scope

The CBI Tehran housing corpus has been corrected to the project lifecycle layout:
87 official PDFs are preserved under `data/raw/housing/cbi/reports/`, while the
101-row extracted monthly workbook remains in `data/interim`. All copied PDFs passed
SHA-256 equality checks. The same byte-identical corpus was copied to the Housing
repository raw layer and the extraction workbook to its staging layer.

The project covers Tehran housing sale price per square metre, TGJU 18-karat gold, fixed income,
and Tehran Stock Exchange equities from 1395/01 through 1405/06. Canonical monthly levels and
returns are retained. The notebook implements an ex-post pilot Stage I risky-sleeve optimization for the
years 1396-1404 and a six-month 1405 YTD period through Shahrivar. Results after 1403/05 use the
documented chain-linked Kilid housing proxy. Stage II is implemented as ex-post risk-aversion
sensitivity, not as an investor-specific allocation recommendation. The principal objective is a
forward-looking optimal portfolio informed by an expert survey; that final stage is not complete.

## Fixed income

اعتماد is the only selected fixed-income source. Bank-deposit and اخزا alternatives were
retired on 2026-09-09 after the window changed to 1395/01–1405/06. Their immutable raw
evidence remains frozen but inactive. The raw TSETMC history
covers 2015-03-14 through 2026-09-07 and every month of 1395 has traded observations.
Its total-return treatment,
distributions, and early non-trading rows still need an issuer and listing audit before returns
are calculated.

## TSE total index

The official TSETMC index API for instrument 32097828799138957 supplies daily observations from
2008-12-04 through 2026-09-07. The canonical panel contains all 126 return months from 1395/01
through 1405/06, based on the final valid TSETMC close in each Jalali month. The annual derivative,
historical collector, and TGJU collector were retired. Their raw files remain frozen inactive
under the immutable-source policy and are not merged with the official series.

## Local inventory

At the initial inventory, no ready-to-use history covered all four assets. As of 2026-09-19,
the separate Housing repository now has an independently built, curated 101-month CBI
Tehran transaction-price series through 1403/05. Its source PDFs and staging workbook have
matching SHA-256 hashes with this project's preserved copies; all 101 CBI-period price levels
match this project's housing panel. This project continues to own its broader four-asset panel
and chain-linked Kilid extension separately.

## Stage

- Asset scope and target window: recorded.
- Fixed-income raw collection: started; selected proxy regime recorded.
- TEDPIX TSETMC raw collection: complete for the active window.
- Canonical level panel: complete, 127 months × four assets, including explicit missing levels.
- Canonical return panel: complete, 126 months × four assets, without filling missing returns.
- CBI housing extraction audit: complete; four source-verified corrections are applied through
  a checked override layer and a 101-row quality report is regenerated with the panels.
- Stage I benchmark-relative risky-sleeve analysis: implemented and numerically validated in the
  notebook for 1396-1404 and 1405/01-06 YTD, with explicit housing-source-regime disclosure.
- Stage II total-portfolio allocation: ex-post mean-variance sensitivity implemented for
  gamma values from 0 through 50 on the documented grid; an investor-specific policy remains
  unspecified.
- Alternative fixed-volatility analysis: implemented at the end of the notebook. One annualized
  covariance model estimated from all 114 aligned months in 1396–1405/06 is reused in every year
  for both Stage I tracking error and Stage II total-portfolio volatility.

## Work required for the final project

- Receive and document the expert survey instrument and its completed responses.
- Analyze the responses and estimate the experts' expected distribution across the four assets.
- Define how those expert views enter the forward-looking return or allocation model.
- Replace the pilot's within-year volatility estimate with a trailing recent-years risk estimate.
  The final lookback length, weighting rule, and minimum history must be selected through research
  and tested without using information that was unavailable at the allocation date.
- Run the revised algorithm and produce the final forward-looking optimal portfolio.

Until these steps are complete, the project status is **in progress**. The data foundation and
historical algorithm run are complete, but the expert-informed forecast and final allocation are not.

## Gold collection

TGJU 18-karat gold daily data has been collected from 1392/04/31 through 1405/06/16 in IRR
per gram. The canonical panel selects the final valid observation in each Jalali month and
calculates adjacent month-end price appreciation. The required 1394/12 endpoint exists, giving
all 126 gold returns from 1395/01 through 1405/06.
Housing uses the official CBI monthly Tehran transaction-price corpus as its primary source.
The 101-row extraction covers 1395/01–1402/12 completely and 1403/01–1403/05 within scope.
Housing uses CBI through 1403/05 and a chain-linked Kilid proxy afterward. The 12-month overlap
does not show close equivalence: level MAPE is 10.97%, maximum absolute level gap is 19.61%,
monthly-return correlation is 0.288, and return MAE is 2.29 percentage points. Kilid is anchored
to CBI at 1403/05 with factor 1.021939953811 and every later row carries a low-similarity flag.
Housing now has 125 valid monthly returns; only 1395/01 remains missing for lack of 1394/12.
The corrected 1397 sequence removes the artificial -99%/+13,000% pair. Its housing returns now
have 4.06% monthly sample volatility and 14.08% annualized volatility. Official revision
disagreements for 1396/12 and 1398/08 remain explicitly flagged under the current-report rule.
