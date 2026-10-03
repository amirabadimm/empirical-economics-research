# Research Status

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
`85.198.48.177` in its existing `investment` database. Coverage is 8,521 price
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
| [Cross-asset allocation](../asset_allocation/docs/STATUS.md) | 126 level months and 125 return months per asset, with missingness retained; historical pilot through 1405/05 | Stage I/II and fixed-covariance sensitivity implemented. Expert survey, trailing-risk design, and final forward-looking allocation pending. |
| [Economic USD/IRR](../economic_usd/docs/STATUS.md) | USD through 1405/06/21; Iranian CPI through 1405/04; liquidity through 1404/12; U.S. CPI through 2026-08 | Data preparation and sparse monthly join implemented. Dollar-liquidity formula and five PPP anchor windows remain to be defined and calculated. |
| [Ahrom options](../options/docs/STATUS.md) | 2026-09-20: 996 verified contracts; 8,903 OptionBaaz rows from 2025-12-17 through 2026-09-20 | Discovery, archive, build, and verification implemented; earlier history remains a material coverage gap. |

Pellet, Bitumen, Rebar, Pista, Warehouse Fees, National Copper / Codal, and the closed
Energy Exchange study retain the recorded checkpoints below. Bitumen now has a processed
diagnostic and distribution; older claims that no processed comparison exists are superseded.

Current certificate/physical Power BI row counts are Copper 206, Zinc 206, Pellet 23,
Rebar 54, Bitumen 31, and Pista 16. Copper, Zinc, Gold, and Pista comparison counts were
checked against local CSVs during this review. Exploratory/provisional labels remain in force.

The latest shared FX checkpoint records 13,103 dates through 1405/07/04 (2026-09-26).
A newer shared input does not imply all consuming outputs were rebuilt. Copper and Zinc
primary comparisons remain bounded by their latest physical anchors, without extrapolation.
Copper, Zinc, and Gold now use signed expanding equal-weight and recency-weighted percentiles
(default 90-calendar-day half-life). Other products retain their empirical distributions.

Root CI runs Ruff and pytest; root pytest discovers `commodity`, `codal`, `energy_exchange`,
`shared`, and `options`. Pista, Asset Allocation, and Economic USD require separate test runs.
This documentation review does not claim a new full-suite, notebook, or report execution.
No recurring collector or NAV scheduler is deployed in the repository.

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
- No collector is currently scheduled or monitored in the repository.

The independent `economic_usd` project now contains reproducible, non-modeled inputs for future USD/IRR research: daily free-market USD through 1405/06/21, monthly Iranian headline urban CPI through 1405/04, monthly CBI liquidity through 1404/12, and complete monthly FRED CPIAUCNS history through 2026-08. PPP and valuation work have not started.

## Update rule

After any change in source, schema, path, formula, observation count, or research stage, update
this file, the project README, and its `docs/WORKFLOW.md`. Detailed operational histories remain
inside each project.
