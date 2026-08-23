# Research Status

Documentation review: 2026-08-23
Latest data checkpoint: 2026-08-22

| Project | Current data coverage | Research stage | Next action |
|---|---|---|---|
| Copper | Certificate through 2026-08-13; FX through 1405/05/20; LME through 2026-08-14; physical through 1405/05/18 | Full valuation pipeline; notebooks refreshed; 102-day forward-gap diagnostic added | Expand analytical QA, regression tests, and refresh monitoring |
| Iron-ore pellet | Certificate through 2026-08-09; physical through 1405/05/18 | Exploratory underlying research | Validate quality/delivery comparability and approve a physical basket |
| Zinc | Certificate through 2026-08-13; physical benchmark through 2026-08-09; LME through 2026-08-14; FX through 1405/05/20 | Full three-bubble pipeline; notebooks refreshed | Interpret notebook results and monitor input freshness |
| Bitumen | Certificate through 2026-08-15; physical through 1405/05/24 | Strict cash–cash diagnostic has 29 overlaps and a major 1405 price discontinuity; no production bubble approved | Verify units/specification, then test exact-date, bounded carry-forward, and lower-frequency alignment rules |
| Warehouse fees | 43 exact-date regimes plus 30 official-table observations back to 2016-10-29 | Official notices, Wayback recovery, and interval builder | Resolve exact boundaries for archived point observations |
| Iran Energy Exchange | 21 certificate symbols; 7,070 rows through 2026-08-22; 1,432 actual traded rows | Feasibility assessment complete; project closed because activity is sparse and concentrated | None; preserve evidence and reproducible collector |

## Available research outputs

- Copper has eight local processed CSVs and an English LaTeX research report under
  `reports/copper/research`.
- Zinc has six local processed CSVs, two analytical notebooks, fourteen tests, and an English
  LaTeX report under `reports/zinc/research`.
- Iron-ore pellet has an exploratory physical-market notebook but no approved benchmark.
- Bitumen has an executed English exploratory notebook covering producer/grade structure, 60/70
  symbol dispersion, settlement missingness, and cash-versus-credit contract pricing. It has no
  approved deliverable basket or processed benchmark yet.
- Warehouse fees has a local 41-row interval CSV and an 11-row live-table snapshot.
- Iran Energy Exchange has a local immutable certificate snapshot and derived activity tables;
  the versioned collector reproduces them. The project is closed and not scheduled for refresh.
- No collector is currently scheduled or monitored in the repository.

## Update rule

After any change in source, schema, path, formula, observation count, or research stage, update
this file, the project README, and its `docs/WORKFLOW.md`. Detailed operational histories remain
inside each project.
