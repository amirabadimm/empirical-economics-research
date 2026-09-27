# Bitumen Research Status

## Shared execution checkpoint (2026-09-22)

The delivered comparison uses the shared engine in `shared/certificate_pipeline`.
Project-specific collectors, builders, and comparison sources are registered in `pipeline.json`.
Run `python refresh_powerbi.py` to rebuild from local sources, add `--collect` to fetch
new available source data first, or add `--plan` to preview the steps without writing.
The existing double-click launcher retains its local-rebuild behavior.
The engine stops on a failed step and publishes the delivery CSV only after all builders succeed.
Product eligibility, alignment methods, and economic interpretation remain product-specific.
Completed software delivery does not itself resolve the economic assumptions documented below.

Bitumen now persists its existing comparison in `data/processed/bubble/bitumen_certificate_bubble.csv`
and builds the same empirical-distribution output as the other products. The original numeric
method and delivery filename are preserved; older statements that no processed comparison exists
are superseded by this checkpoint.

Last updated: 2026-09-19
Stage: exploratory domestic 60/70 cash-cash diagnostic; no approved bubble

The 31 exact-date diagnostic rows are reproducible through the project-local `refresh_powerbi.cmd` and exported to `outputs/power_bi/bitumen_certificate_physical_comparison.csv` for Power BI. They remain unapproved comparisons.

Official incremental collection reached 286 certificate rows through 2026-09-17
(208 traded days) and 47,191 broad physical rows through 1405/06/28
(24,201 positive trades). The refreshed Plotly notebook executed all 18 code cells.

The conservative standard-cash/observed-cash filter has 32 physical dates and 31 exact
positive-certificate overlaps through 1405/06/15. The 1405 subset has 16 dates and a
161.79% median certificate/physical difference. This is a diagnostic, not an arbitrage
or production valuation: official certificate units, quotation basis, grade, delivery,
fees and taxes remain to be reconciled. Static reports retain their earlier data vintage.
