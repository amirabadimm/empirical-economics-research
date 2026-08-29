# Iron-Ore Pellet Certificate Research

## Research question

What premium or discount does the Iranian iron-ore pellet warehouse receipt trade at relative to
a defensible benchmark built only from comparable domestic physical pellet trades?

## Current checkpoint

- Data checkpoint: 2026-08-10
- Certificate: 268 calendar observations, 194 positive-trading days, through 2026-08-27
- Physical market: 3,535 rows, including 1,658 positive trades, through 1405/06/07
- Stage: exploratory exact-date certificate-bubble series implemented and validated
- Selected: Gol Gohar (`GOLG-PELL-00`) and Gohar Zamin (`GHZ-PELL-00`)
- Excluded for lower representation across all positive physical trades since certificate start: Sangan Khorasan (5.66%) and Chadormalu (9.81%)
- Notebook benchmark: every strict-cash day with at least one selected producer; one available price or the simple mean when both trade
- Exact-date overlap with positive certificate trading: 22 days (16 single-producer, 6 two-producer)
- Processed benchmark file: not yet produced; the current bubble series is notebook-based and exploratory
- The only positive observation is 1404/10/21 (+11.03%); it is retained but flagged as a single-producer, composition-sensitive benchmark. See reports/FINAL_REPORT.md.
- Complete English LaTeX report: `reports/pellet_certificate_report.tex`
- Reproducible report figures: run reports/build_report_figures.py from the project directory

The physical raw scope retains every normalized iron-ore-pellet row; screening does not alter raw
data. The four initially reviewed producers were not a homogeneous price group. Gol Gohar and
Gohar Zamin were the closest pair and jointly represented 53.86% of all positive physical volume
since certificate trading began. The notebook now assesses this two-producer domestic benchmark. No
external intrinsic-value model is in scope.

## Reproduction from the repository root

Canonical physical and certificate records remain separate under `data/raw/{physical,certificate}`.
Future physical tables use `data/processed/physical`; any approved bubble uses
`data/processed/bubble`.

```powershell
python .\commodity\pellet\src\pellet\collectors\certificate.py
python .\commodity\pellet\src\pellet\collectors\physical.py
```

See [`docs/WORKFLOW.md`](docs/WORKFLOW.md) for provenance, validation, and the unresolved
benchmark construction and validation details.
