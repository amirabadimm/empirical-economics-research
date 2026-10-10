# Research Status

Asset Allocation refreshed canonical REIT and TEDPIX histories through 2026-10-07 and shared USD/IRR through Jalali 1405/07/16 on 2026-10-10; Kilid had no new complete month. A completed-week cutoff correction moved the rebuilt REIT comparison to 2026-10-09. The notebook and four LaTeX reports were regenerated; the 80-cell grid retains 66 reportable coefficients. See the project status for current returns, different housing endpoints, and verification. Earlier REIT performance figures below are superseded.

Asset Allocation added a detailed Persian REIT report on 2026-10-08 at `asset_allocation/reports/REIT_DETAILED_REPORT_FA.tex`, alongside the short Persian and English versions. It includes performance, distributions, all active correlation grids and monthly allocation/return appendices. Its housing-exposure conclusion is explicitly limited to the observed period.

Asset Allocation added a separate Persian management brief on 2026-10-08 at `asset_allocation/reports/REIT_MANAGEMENT_BRIEF_FA.tex`. It uses Amiri, RTL prose/tables and LTR numeric spans, with concise correlation and asset-composition findings followed by three tables. Existing processed inputs were used; PDF rendering is not verified locally.

Asset Allocation added `reports/REIT_MANAGEMENT_BRIEF.tex` on 2026-10-08 as a concise companion to the detailed REIT report, with findings first and three supporting tables at the end. It uses the existing research checkpoint without refreshing data.

Asset Allocation expanded its single English LaTeX REIT performance report on 2026-10-08 with benchmark shortfalls, relative wealth, drawdowns, full allocation histories, management-attribution limits, complete two-year returns, regression diagnostics, and the 80-cell coverage appendix. Existing processed data were used without a source refresh. The source is self-contained for translation; PDF compilation is unverified because no local TeX engine is available.

Asset Allocation's cumulative Plotly chart allocation bands were made explicitly faint on 2026-10-08 after the previous stack-group fill rendered too opaque. The notebook was reexecuted; no source or derived data changed. The fund mix dropdown and weekly return lines remain active.

Asset Allocation's cumulative-return notebook chart gained selectable month-end asset-mix shading for Arzesh Maskan and Danik on 2026-10-07. A preserved user-supplied Codal-derived workbook supplies 48 validated monthly rows through 1405/06; three carry source quality flags. This was a new source snapshot and processed derivative, not a market or housing canonical refresh. The nine-figure notebook was reexecuted; weekly return lines and prior correlation grids remain on their existing frequencies. See the project status for the source hash and verification limits.

Asset Allocation's active REIT report changed to a single LaTeX source on 2026-10-06: `asset_allocation/reports/REIT_CROSS_ASSET_ANALYSIS.tex`. It includes cumulative returns, recorded dividend events, traded-versus-reinvested results, all six correlation grids with pair counts, predictive regression, and computed conclusions. The HTML/Markdown report and generator were removed; the Plotly notebook remains the interactive analysis. This was a presentation rebuild from processed data, not a canonical source refresh. Earlier HTML report descriptions below are superseded.

Asset Allocation consolidated its REIT comparisons on 2026-10-06 into six frequency-matched Plotly heatmaps and a single 80-cell derived grid. TEDPIX is compared daily, weekly, and monthly; Tehran housing monthly; USD/IRR daily and at 4/13/26-week leads of REIT returns. Sixty-six cells are reportable after minimum five-pair and 70% coverage rules. Kakh remains in qualifying daily/weekly cells and is suppressed in thin long windows. The active notebook has nine Plotly figures and the local report has eight. Housing has no daily or weekly source, so none was imputed. No canonical source was refreshed; earlier heatmap/window counts below are superseded.

Asset Allocation refreshed its same-period correlations on 2026-10-06. The active notebook now has eight Plotly figures, including weekly USD/IRR, weekly TEDPIX, and monthly Tehran housing heatmaps for trailing 1, 3, 6, 12, and 24 months. The two-year cumulative chart excludes Kakh, and the predictive table omits FDR. The 24-month housing sample has 21–22 observed pairs for the three longer-history funds because REIT returns are missing in some months; these gaps are not filled. The local HTML report has seven charts. The earlier figure counts and FDR descriptions below are superseded; no canonical source was refreshed by this analysis change.

Asset Allocation added a no-lag monthly correlation of its four reconstructed REIT returns with Tehran housing through 1405/06. Three funds have 21–22 paired months and report Pearson coefficients; Kakh has four and is suppressed. The active notebook now has five Plotly figures, and the regenerated local report has four interactive plots plus the versioned Markdown summary. This 2026-10-06 analysis build changed only processed derivatives and presentation artifacts, not canonical market sources. Earlier plot counts below are superseded.

Asset Allocation now has a generated interactive REIT/USD report and a versioned Markdown companion, built on 2026-10-06 from processed data ending 2026-10-02 (housing: 2026-09-22). The report contains three Plotly charts, cumulative and payout-event tables, the common-week lag estimates, and the three reportable predictive models. Report generation did not refresh raw sources.

Documentation review 2026-10-06: the workspace and Asset Allocation workflow documents now use the current four-fund run order and mark earlier three-fund analyses as historical. This documentation-only change did not refresh market data.

Asset Allocation's active four-REIT notebook now has 12 cells and four Plotly figures. Its new 24-Jalali-month USD lag panel has 15 reportable of 20 fund/lag correlations on common per-fund weeks; Kakh's five are suppressed for only 16 pairs. Three fund-level predictive regressions meet the 52-week minimum, with HAC(4) joint USD tests and FDR-adjusted p-values; Kakh has 18 complete rows and is omitted. The previous 10-cell/three-figure heatmap checkpoint below is superseded.

The compact active Asset Allocation REIT notebook now includes Kakh, has 10 cells and three Plotly figures, and uses custom reinvested-value returns throughout. The derived daily fund panel has 2,052 sessions; the two-year six-asset weekly comparison has 630 rows. Of 64 same-period correlation cells, 42 meet the 12-weekly or 6-monthly-pair rule. Earlier three-fund and low-count correlation views below are superseded for the active notebook.

The Asset Allocation active three-REIT cumulative chart now uses a custom assembly-date dividend-reinvestment scenario from traded closes. Its three user-supplied events generate 1,948 daily derived rows and a 525-row two-year weekly comparison across Kelid, Danik, Arzesh Maskan, TEDPIX, and USD/IRR. The previous exchange-adjusted REIT cumulative checkpoint below is superseded for the active view. Existing correlation tables remain traded-price based pending review.

Asset Allocation's Kilid source was refreshed on 2026-10-06. Its validated canonical raw housing CSV has 37 complete months through 1405/06, and its rebuilt four-asset panel has 127 level and 126 return months. The 24-point monthly housing Plotly overlay now ends on 2026-09-22. Earlier 1405/05 housing endpoints below are superseded.

## Asset-allocation real estate fund extension — 2026-10-05

Eight fund price histories and TEDPIX were refreshed through 2026-10-04. A separate monthly return panel and combined correlation/regression notebook are complete. The current incomplete month is excluded; cash distributions and corporate actions still require audit before the fund series can be called total returns. The original four-asset optimization sample was subsequently extended through 1405/06 with the Kilid refresh.

The 1, 3, 6, 12, 24, and 48-month trailing comparison and OLS regression table are complete through 1405/06, with 48 fund-window rows and Plotly notebook views.

The combined English-language notebook now includes weekly returns through Friday 2026-10-02 from a bounded 24-month lookback, with 40 fund/window correlation and regression estimates.

The shared USD/IRR collector refreshed its canonical series to 13,110 dates through 2026-10-04. Asset Allocation now has a separate 102-return weekly USD panel and 40 fund/window USD regression rows through 2026-10-02; the original TEDPIX analysis is unchanged. The USD comparison reports legacy-midpoint versus TGJU-close source-method counts.

Asset Allocation's final Plotly notebook section now has a 105-week, ten-asset cumulative level-change panel through 2026-10-02 using validated exchange-adjusted fund prices. Its baseline summary distinguishes full-window assets from three later-listed funds; the derived panel has 1,050 rows. The older unadjusted fund cumulative values are superseded. Plotly bridges missing weeks visually without filling the processed data; payout treatment awaits a fund-level audit. The same chart overlays 24 monthly Tehran housing observations through 2026-09-22 from a separate flagged Kilid proxy panel (+160.7% price appreciation since 2024-10-21); housing is not extrapolated to the weekly endpoint.

On 2026-10-06 the active notebook was renamed `asset_allocation/notebooks/iran_reits_cross_asset_analysis.ipynb` and narrowed to Arzesh Maskan, Kelid, and Danik. Its final Plotly section adds zero- versus one-prior-day/week/Jalali-month USD correlations across six trailing windows. The three-fund processed lag table has 108 cells (96 valid) and 4,964 return-pair rows. Earlier ten-asset and eight-fund counts describe retained processed source panels, not the active notebook view. The dividend-reinvested return audit remains incomplete.

The notebook now also compares Kelid, Arzesh Maskan, and Danik traded versus exchange-adjusted prices in Plotly. A separate eight-fund cash-reinvestment builder contains two verified annual payments, for Kelid and Malek Atiyeh. Remaining payout source coverage is incomplete; its known-payment paths are not certified complete dividend-reinvested total returns. Arzesh Maskan's equal adjusted and traded series must not be read as a no-dividend finding.
The historical payout audit now lists first traded-date coverage and earlier annual-payment gaps for all eight funds in `asset_allocation/docs/REIT_DIVIDEND_AUDIT.md`. It distinguishes pre-baseline distributions from payments inside the two-year comparison and records that 1,640 IRR discussed for Danik in 1403 was audited earnings per unit, not verified cash paid.

## Gold scheduled monitoring deployed — 2026-10-03

Five-minute disposable price/NAV cache and four daily-history ranks are deployed
with enabled daily and weekly source-refresh timers. Live polls run only
12:00-18:00 Tehran and never enter daily history. Fresh readings and four deciles
returned for all five funds; expiry filtering and off-hours scheduling were checked.
The first server daily refresh succeeded: 8,531 prices through September 30,
18,051 selected NAV rows through September 29 for Ayar / October 2 for others,
and 8,213 bubbles through September 29 for Ayar / September 30 for others.
This supersedes the initial server counts below. Local workstation sources,
processed presentations and notebooks retain their prior checkpoints.

## Initial Gold database deployment (superseded by scheduled refresh above) — 2026-10-03

The five-fund PostgreSQL schema and transactional loader are deployed to
a private deployment host in its existing `investment` database. Coverage is 8,521 price
rows, 18,032 NAV rows and 8,202 bubbles. Source transfer hashes and repeat-load
analytical values were verified. The September 29 market-data checkpoint remains
unchanged at this initial checkpoint; scheduled monitoring above supersedes it.

## Gold phase closeout — 2026-10-03

The September 29 five-fund gold collection, builds, and NAV reliability audit
are accepted as the completed research checkpoint. Minor NAV gaps and Gohar
manager disagreements remain documented per date; Mesghal remains excluded.
Incremental collection and periodic full-history checks are maintenance.
This closeout changes stage status only; it does not claim a newer data refresh.

## Gold incremental collection — 2026-09-29

The gold routine now requests the latest 30 TSETMC price rows and the Fipiran
recent NAV window; initial loads and `--full` request complete history. All five
live recent refreshes and dependent rebuild/audits passed. Current two-year
NAV matches are Ayar 448/465, Tala 465/465, Kahroba 464/465, Ganj 462/465,
and Gohar 464/464. See the gold workflow
for the periodic full-history revision check. Other commodity pipelines were not
changed.


## Ayar Fipiran collection and rebuild - 2026-09-29

Selected source: Fipiran, registration 11586 / group 0, `cancelNav` in IRR.
Fresh collection: 2,997 unique NAV dates, 2018-06-20 through 2026-09-26.
Two-year window ending 2026-09-28: 448/465 traded dates covered, 17 missing.
Full-history bubble: 1,928 exact-date observations through 2026-09-26.
Archived-source audits were replayed after the rebuild: all 337 two-year traded
dates shared with saved TSETMC NAV agree exactly. The 111 additional covered
trading dates are not all independently corroborated. Mofid was not queried.
Previous TSETMC and Mofid files remain separate evidence. Other fund canonical
sources and shared code were not changed; the gold notebook was not executed.
This supersedes the earlier Ayar TSETMC selection and its 337/465, 1,536-row build.


## Earlier gold reliability audit (Ayar build superseded) — 2026-09-29

Tala, Kahroba, and Ganj's selected Fipiran histories match current manager records
on every shared two-year date; Kahroba has one missing traded NAV and Ganj three.
Gohar has three manager disagreements, two on trading dates; September 9 materially
changes the premium. Its unit count also changes 80-fold on September 27.
Ayar TSETMC collection/rebuild now succeeded with 337/465 two-year matches and
1,536 full-history bubble rows through September 8. This incomplete source
supersedes both the pending transition and the earlier Mofid-based Ayar counts.
See [the report](../commodity/gold/docs/NAV_RELIABILITY.md). This was a gold-only
validation; other project checkpoints remain unchanged.

## Mesghal historical NAV recheck — 2026-09-29

Gold's live Mesghal identity check passed for registration 11899 / group 2, but
Fipiran history returned `[]`. TSETMC history was labelled نقرات and rejected;
only current Mesghal NAV was obtained. No historical dataset or new analysis was
published. Responses are archived and a reproducible investigation is documented
in [the gold validation report](../commodity/gold/docs/MESGHAL_NAV_VALIDATION.md).

## Superseded pending Gold Ayar transition — earlier on 2026-09-29

Ayar now selects TSETMC historical NAV in code, but live collection failed in this
environment. Existing Mofid-based Ayar processed outputs and 464/464 coverage
are superseded until TSETMC collection and rebuild succeed. The September 28
gold checkpoint below records the prior source selection.

## Current workspace review — 2026-09-28

This review reconciles project documentation, refresh entry points, pipeline manifests,
and available local comparison CSVs. It did not collect new data or rebuild research outputs.
The current checkpoints below supersede the historical September 19–22 summary retained
later in this file. Data coverage differs by project.

| Project | Current checkpoint | Stage / next action |
|---|---|---|
| [Copper](../commodity/copper/docs/STATUS.md) | Refreshed 2026-09-27: 293 certificate rows through 2026-09-26; 1,175 physical rows; 799 eligible physical dates; 206 primary comparisons through 2026-09-20 | Production and research outputs rebuilt; monitor freshness and analytical QA. Global Copper / COCHILCO research is cancelled, with evidence preserved. |
| [Zinc](../commodity/zinc/docs/STATUS.md) | Refreshed 2026-09-26: raw certificate through 2026-09-24; 213 certificate/intrinsic dates; 563 physical benchmark dates; 206 primary comparisons through 2026-09-20 | Approved 99.97/99.98 basket and bounded valuation. Research-only regression and historical studies were not refreshed. |
| [Gold ETFs](../commodity/gold/docs/STATUS.md) | 2026-09-28 active two-year build: Ayar 464/464, Tala 464/464, Kahroba 463/464, Ganj 461/464, Gohar 463/463 traded dates with exact NAV | Gohar replaces Mesghal; Zarvan begins too late for two years. Mesghal investigation retained; Ayar bubble has 1,949 matched dates through 2026-09-27. |
| [Silver](../commodity/silver/docs/STATUS.md) | 2026-09-27 scaffold: collectors, strict benchmark, exact-date diagnostic, distribution, refresh entry point, and tests | No data collected or economic benchmark approved. Source validation and comparability review remain pending. |
| [Cross-asset allocation](../asset_allocation/docs/STATUS.md) | 127 level months and 126 return months per asset, with missingness retained; historical pilot through 1405/06 | Stage I/II and fixed-covariance sensitivity implemented. Expert survey, trailing-risk design, and final forward-looking allocation pending. |
| [Economic USD/IRR](../economic_usd/docs/STATUS.md) | USD through 1405/06/21; Iranian CPI through 1405/04; liquidity through 1404/12; U.S. CPI through 2026-08 | Data preparation and sparse monthly join implemented. Dollar-liquidity formula and five PPP anchor windows remain to be defined and calculated. |
| [Ahrom options](../options/docs/STATUS.md) | 2026-09-20: 996 verified contracts; 8,903 OptionBaaz rows from 2025-12-17 through 2026-09-20 | Discovery, archive, build, and verification implemented; earlier history remains a material coverage gap. |

Pellet, Bitumen, Rebar, Pista, Warehouse Fees, National Copper / Codal, and the closed
Energy Exchange study retain the recorded checkpoints below. Bitumen now has a processed
diagnostic and distribution; older claims that no processed comparison exists are superseded.

Current certificate/physical Power BI row counts are Copper 206, Zinc 206, Pellet 23,
Rebar 54, Bitumen 31, and Pista 16. Copper, Zinc, Gold, and Pista comparison counts were
checked against local CSVs during this review. Exploratory/provisional labels remain in force.

The earlier shared FX checkpoint of 13,103 dates through 1405/07/04 (2026-09-26) is superseded by the 2026-10-05 refresh recorded above.
A newer shared input does not imply all consuming outputs were rebuilt. Copper and Zinc
primary comparisons remain bounded by their latest physical anchors, without extrapolation.
Copper, Zinc, and Gold now use signed expanding equal-weight and recency-weighted percentiles
(default 90-calendar-day half-life). Other products retain their empirical distributions.

Root CI runs Ruff, the root pytest suite, the dedicated Pista tests, and the network-free
Asset Allocation collector tests. Data-dependent Asset Allocation checks and Economic USD
contracts remain documented project-level validations rather than clean-clone CI requirements.
This documentation review does not claim a new notebook or report execution. Gold's versioned
systemd timers are deployed; other project collectors remain manual unless their own status says otherwise.

## Historical workspace summary (September 19–22, 2026)

Counts and stages in the following sections describe those earlier checkpoints; use the
current review above and linked project status files for subsequent changes.

## Certificate integration checkpoint (2026-09-22)

All six certificate products use the shared execution and delivery engine. Rebuilding
from existing sources reproduced all six prior Power BI files byte-for-byte. Bitumen
now also writes its processed comparison and empirical distribution. Source-collection
plans have been checked; live online collection was not part of this verification.
Economic methodology and comparability labels were preserved.

Documentation review: 2026-08-29
Latest data checkpoint: 2026-09-19

The prior options research project was retired on 2026-09-20. Its code, documentation,
and derived analysis were removed. The former project-local raw directory is no longer present.
An independent Ahrom options pipeline discovered 996 contracts and collected 8,903
OptionBaaz daily rows from 2025-12-17 onward; see `options/docs/STATUS.md` for
the substantial earlier-history gap.

Each certificate/physical product now has its own Power BI delivery CSV at `outputs/power_bi/<product>_certificate_physical_comparison.csv` and a local `refresh_powerbi.cmd` that rebuilds it from existing raw inputs. Current row counts are copper 201, zinc 201, pellet 23, rebar 54 (two explicitly distinct comparisons), bitumen 31 (unapproved diagnostic), and pistachio 16 (provisional weekly-price proxy). Analytical calculation tables remain in `data/processed`; warehouse fees have no certificate/physical comparison.

Workspace-wide USD/IRR is a single shared canonical input with 13,096 dates through 1405/06/26;
Copper and Zinc no longer maintain project-local copies.

Full-market IME physical responses now have a content-addressed shared owner. The 1,593 existing
local snapshots remain frozen pre-consolidation evidence. Copper/Zinc LME collection and intrinsic
regression now use shared engines with explicit commodity wrappers.

Seven active commodity notebooks now include the same governed responsive Plotly market-dashboard section. Rebar
adds all-record physical `GoodsName` counts, separate physical/certificate activity views, a
strict 5-observation exact-date A3 / 18 mm exploratory bubble, and a clearly marked 49-observation
A3 / 12 mm cross-diameter sensitivity.

| Project | Current data coverage | Research stage | Next action |
|---|---|---|---|
| Copper | 286 certificate rows through 2026-09-17; 1,174 physical rows through 1405/06/22 | Domain-separated physical/bubble pipeline; certificate notebook executed; static report retains its prior checkpoint | Expand analytical QA and refresh monitoring |
| Iron-ore pellet | 286 certificate rows through 2026-09-17; 3,588 physical rows through 1405/06/23 | Exploratory underlying research; 23 exact-date bubbles; Plotly notebook refreshed | Validate quality/delivery comparability and approve a physical basket |
| Zinc | 286 certificate rows through 2026-09-17; 6,398 physical rows through 1405/06/25 | Domain-separated three-bubble pipeline; Plotly notebooks refreshed; static report at prior checkpoint | Interpret results and monitor input freshness |
| Bitumen | 286 certificate rows through 2026-09-17; 47,191 physical rows through 1405/06/28 | Strict cash-cash diagnostic has 31 overlaps and a major 1405 price discontinuity; Plotly notebook refreshed; no production bubble approved | Verify units/specification before economic interpretation |
| Steel rebar | 31,953 physical rows through 1405/06/28; 286 certificate rows through 2026-09-17 | A3/18 exact-date exploratory bubble: 5 observations; marked A3/12 cross-diameter sensitivity: 49 | Verify official specification, units, eligibility, delivery and costs before benchmark approval |
| Pista | 21 certificate rows through 2026-09-17; 16 traded days; Abtahi workbook has 578 weekly rows | Audit flags 55 product observations; notebook plots 16 bounded weekly-proxy premiums | Confirm price units and product specification; resolve manual-review flags before inference |
| Warehouse fees | 32,290 daily rows through 2026-09-19; 43 exact-date regimes plus 30 archived official-table observations | Official notices, Wayback recovery, and interval builder | Resolve exact boundaries for archived point observations |
| Iran Energy Exchange | 21 certificate symbols; 7,070 rows through 2026-08-22; 1,432 actual traded rows | Feasibility assessment complete; project closed because activity is sparse and concentrated | None; preserve evidence and reproducible collector |
| National Copper — Codal | 75 valid core quarters; 18 complete years; labor fields provisional | Core modern-plus-legacy history validated; labor audit pending | Build header-aware labor parser and reconcile non-monotonic cumulative values |

## Available research outputs

- Copper processed CSVs are separated into `physical`, `bubble`, and `analysis` domains and have an English LaTeX research report under
  `reports/copper/research`.
- Zinc processed CSVs are separated into `physical` and `bubble` domains, with two analytical notebooks and an English
  LaTeX report under `reports/zinc/research`.
- Iron-ore pellet has an exploratory physical-market notebook but no approved benchmark.
- Bitumen has an executed English exploratory notebook covering producer/grade structure, 60/70
  symbol dispersion, settlement missingness, and cash-versus-credit contract pricing. It has no
  approved deliverable basket or processed benchmark yet.
- Warehouse fees has a 32,290-row daily processed CSV through 2026-09-19, built from 43
  exact official fee events and 30 archived observations; historical event boundaries remain
  explicitly incomplete.
- Iran Energy Exchange has a local immutable certificate snapshot and derived activity tables;
  the versioned collector reproduces them. The project is closed and not scheduled for refresh.
- National Copper Codal research has a local immutable archive of 118 modern qualifying filings
  plus two verified legacy PDFs and a single 75-row quarterly core history. Five
  unavailable quarters are documented. Labor fields are explicitly provisional pending a
  schedule-layout and cumulative-reconciliation audit.
- Gold has deployed live, daily, and weekly systemd refresh timers; other project collectors remain manual at this checkpoint.

The independent `economic_usd` project now contains reproducible, non-modeled inputs for future USD/IRR research: daily free-market USD through 1405/06/21, monthly Iranian headline urban CPI through 1405/04, monthly CBI liquidity through 1404/12, and complete monthly FRED CPIAUCNS history through 2026-08. PPP and valuation work have not started.

## Update rule

After any change in source, schema, path, formula, observation count, or research stage, update
this file, the project README, and its `docs/WORKFLOW.md`. Detailed operational histories remain
inside each project.
