# Iron-Ore Pellet Certificate: Final Exploratory Report

Last updated: 2026-08-15

## Objective and scope

This study estimates the premium or discount of the Iranian iron-ore pellet warehouse receipt relative to comparable domestic physical pellet transactions. It deliberately excludes global prices, exchange rates, and external intrinsic-value models. Raw files and immutable source snapshots are not modified.

## Physical-market selection

Producer selection is based on all positive physical-market trades since certificate inception, independent of contract and settlement type. Gol Gohar and Gohar Zamin jointly account for 53.86% of this volume. Chadormalu and Sangan Khorasan jointly account for 15.47% and are excluded because of lower market representation—not simply because their prices differ or overlap is sparse.

Benchmark construction is stricter. It accepts only cash or cash-matching contracts with an explicitly cash settlement and positive executed price and quantity. Cash/credit transactions are excluded.

## Benchmark rule

A date is eligible when at least one selected producer has a qualifying cash trade. The daily benchmark is the observed price when only one producer trades and the simple mean when both trade. Certificate comparisons are exact-date only and require positive certificate volume and price. Neither interpolation nor carry-forward prices are used.

The final sample contains 22 observations: 16 single-producer and six two-producer days. The certificate bubble has a mean of -12.18%, a median of -11.55%, a minimum of -24.93%, and a maximum of +11.03%. Only one observation is positive.

## Positive-bubble case study: 1404/10/21

| Market observation | Price (IRR/kg) |
|---|---:|
| Gol Gohar qualifying cash trade and official benchmark | 94,566 |
| Warehouse-receipt certificate | 104,998 |
| Gol Gohar forward cash/credit trade | 107,332 |
| Gohar Zamin cash/credit trade | 111,229 |

The official bubble is +11.03%. Gohar Zamin is correctly excluded because its settlement is cash/credit. As a sensitivity check only, averaging the two same-day producer prices produces a benchmark of IRR 102,897.5/kg and a bubble of approximately +2.04%. Roughly nine percentage points of the official result are therefore sensitive to benchmark composition.

Certificate settlement had already risen from IRR 81,844/kg on 1404/10/10 to IRR 103,483/kg on 1404/10/17, about 26.4%. On 1404/10/21, 208,726 certificates traded between IRR 103,500 and 105,560/kg and settlement increased by 6.99%. The result is not driven by a single low-volume print.

A plausible interpretation is a timing difference in price discovery: the continuously traded certificate may have adjusted before the intermittently supplied physical market. Its position between the qualifying cash price and same-day forward/credit prices is consistent with that interpretation. No contemporaneous public event establishes causality, so this remains a data-based inference.

## Reporting rule and limitations

The observation is retained because both trades are valid, but it must be labeled as a composition-sensitive, single-producer benchmark. Results should separate single- and two-producer days and include the sensitivity check. With 16 of 22 observations based on one producer, structural conclusions require broader time coverage.

## Reproducibility

- Certificate input: `data/raw/certificate/pellet_certificate_raw.csv`
- Physical input: `data/raw/physical/pellet_physical_raw.csv`
- Analysis: `notebooks/01_physical_analysis.ipynb`
- Scope and validation: `docs/WORKFLOW.md`
- Figure builder: `reports/build_report_figures.py`

Public news reviewed for the 1404/10/17 context provides background only and is not evidence of causality.
