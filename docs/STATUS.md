# Research Status

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
