# Copper output ownership

## Routine product

Run `python commodity/copper/refresh_powerbi.py` from the workspace root.
Add `--collect` to fetch sources; otherwise only local inputs are used.

| Output under data/processed | Owner | Role |
|---|---|---|
| physical/nci_copper_cash_daily.csv | build_physical_benchmark.py | Physical benchmark |
| bubble/copper_certificate_bubble.csv | build_certificate_bubble.py | Primary certificate/physical result |
| bubble/certificate_vs_intrinsic_bubble.csv | build_intrinsic_bubbles.py | Supporting certificate/intrinsic result |
| bubble/physical_vs_intrinsic_bubble.csv | build_intrinsic_bubbles.py | Supporting physical/intrinsic result |
| bubble/copper_bubble_distribution.csv | build_bubble_distribution.py | Distribution of the three results |

`build_valuation.py` prepares inputs once through `valuation_inputs.py`, then calls
both builders. Individual builder commands remain compatible. CSV publication uses
`common.write_atomic`: atomic per file, not a transaction over the output set.
Resolve any failed refresh before treating the set as a new checkpoint.

The Power BI CSV under `outputs/power_bi` is a delivery view. Copper spread and
percentage are copied from the canonical result and checked against the exported
prices with a 0.000001 tolerance.

## Research support (excluded from routine refresh)

| Output | Builder under src/copper/processing |
|---|---|
| bubble/intrinsic_regression.csv and intrinsic_regression_metrics.csv | build_intrinsic_regression.py |
| physical/nci_copper_forward_gap.csv | build_forward_gap_analysis.py |
| analysis/presentation_timeline_daily.csv and presentation_timeline_events.csv | build_presentation_timeline.py |

These are research checkpoints. Run their builder explicitly when revisiting the
analysis; presence does not imply freshness. Notebook appendix calculations are
exploratory and do not publish canonical results.

## Report

Run `python reports/copper/research/build_figures.py` after refreshing the product.
Compile `copper_research_report.tex` from that report directory. Three independent
charts place the primary comparison first; statistics are generated in the figures.
