# Research Status

Documentation review: 2026-08-29
Latest data checkpoint: 2026-08-29

Workspace-wide USD/IRR is a single shared canonical input with 13,079 dates through 1405/06/05;
Copper and Zinc no longer maintain project-local copies.

Full-market IME physical responses now have a content-addressed shared owner. The 1,593 existing
local snapshots remain frozen pre-consolidation evidence. Copper/Zinc LME collection and intrinsic
regression now use shared engines with explicit commodity wrappers.

Seven active commodity notebooks now include the same governed responsive Plotly market-dashboard section. Rebar
adds all-record physical `GoodsName` counts, separate physical/certificate activity views, a
strict 5-observation exact-date A3 / 18 mm exploratory bubble, and a clearly marked 46-observation
A3 / 12 mm cross-diameter sensitivity.

| Project | Current data coverage | Research stage | Next action |
|---|---|---|---|
| Copper | 268 certificate rows through 2026-08-27; 1,171 physical rows through 1405/06/02 | Domain-separated physical/bubble pipeline; notebooks and reports refreshed | Expand analytical QA and refresh monitoring |
| Iron-ore pellet | 268 certificate rows through 2026-08-27; 3,535 physical rows through 1405/06/07 | Exploratory underlying research; 23 exact-date bubbles | Validate quality/delivery comparability and approve a physical basket |
| Zinc | 268 certificate rows through 2026-08-27; 6,325 physical rows through 1405/06/04 | Domain-separated three-bubble pipeline; notebooks and reports refreshed | Interpret results and monitor input freshness |
| Bitumen | Certificate through 2026-08-15; physical through 1405/05/24 | Strict cash–cash diagnostic has 29 overlaps and a major 1405 price discontinuity; no production bubble approved | Verify units/specification, then test exact-date, bounded carry-forward, and lower-frequency alignment rules |
| Steel rebar | 31,641 physical rows through 1405/06/07; 268 certificate rows through 2026-08-27 | A3/18 exact-date exploratory bubble: 5 observations; marked A3/12 cross-diameter sensitivity: 46 | Verify official specification, units, eligibility, delivery and costs before benchmark approval |
| Warehouse fees | 43 exact-date regimes plus 30 official-table observations back to 2016-10-29 | Official notices, Wayback recovery, and interval builder | Resolve exact boundaries for archived point observations |
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
- Warehouse fees has a local 41-row interval CSV and an 11-row live-table snapshot.
- Iran Energy Exchange has a local immutable certificate snapshot and derived activity tables;
  the versioned collector reproduces them. The project is closed and not scheduled for refresh.
- National Copper Codal research has a local immutable archive of 118 modern qualifying filings
  plus two verified legacy PDFs and a single 75-row quarterly core history. Five
  unavailable quarters are documented. Labor fields are explicitly provisional pending a
  schedule-layout and cumulative-reconciliation audit.
- No collector is currently scheduled or monitored in the repository.

## Update rule

After any change in source, schema, path, formula, observation count, or research stage, update
this file, the project README, and its `docs/WORKFLOW.md`. Detailed operational histories remain
inside each project.
