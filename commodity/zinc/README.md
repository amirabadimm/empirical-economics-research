# Zinc Certificate Valuation

## Valuation presentation (2026-09-23)

The valuation notebook opens with the approved certificate-to-physical bubble.
Certificate-to-intrinsic and physical-to-intrinsic comparisons each have a separate
supporting chart. Intrinsic value is LME cash USD/kg multiplied by USD/IRR.
Shared dashboards explicitly select these three approved outputs, primary first;
experimental regression files are not mixed into the headline chart.
Historical investigations remain in a labeled research appendix. No valuation
formula, source data, or project completion status changed in this presentation update.

Double-click `refresh_powerbi.cmd` in this project to rebuild its physical benchmark, comparison, and `outputs/power_bi/zinc_certificate_physical_comparison.csv` for Power BI from existing raw inputs.

## Research question

How does the Iranian zinc-ingot warehouse receipt trade relative to an eligible domestic
physical basket and to an LME–FX intrinsic benchmark?

## Current checkpoint

- Data checkpoint: 2026-09-19
- Certificate: 288 calendar observations, 210 positive-trading days, through 2026-09-20
- Broad physical raw data: 6,398 rows, including 3,581 positive trades, through 1405/06/25
- LME cash zinc: 4,733 observations from 2008-01-02 through 2026-09-18
- Shared free-market USD/IRR: 13,096 observations through 1405/06/26
- Official physical benchmark: 563 days from 2009-08-16 through 1405/06/29
- Test suite: 14 network-free contract and pipeline tests

## Comparable physical underlying

Broad raw data intentionally retain both zinc ingot and zinc soil for auditability. Zinc soil
is economically distinct and never enters the ingot benchmark. The approved underlying is a
volume-weighted daily basket of 99.97 and 99.98 zinc ingots traded through cash or cash-matching
contracts with positive executed price and quantity.

The primary method interpolates the physical/intrinsic ratio between exact certificate/physical
anchors without extrapolation. Three measures are reported separately: physical versus intrinsic,
certificate versus intrinsic, and certificate versus estimated domestic physical value.

## Main current result

The primary output contains 206 modeled certificate days from 2025-10-26 through 2026-09-20:
50 observed anchors and 156 interpolated days. The certificate premium to estimated domestic
physical value averages 0.80%, compared with an average direct certificate/intrinsic discount
of 20.54%. This difference demonstrates the economic importance of the domestic physical basis.

## Reproduction from the repository root

Canonical physical and certificate trades remain separate under `data/raw/{physical,certificate}`.
The physical benchmark is written to `data/processed/physical`; every bubble and regression table
is written to `data/processed/bubble`.

```powershell
python .\commodity\zinc\src\zinc\collectors\certificate.py
python .\commodity\zinc\src\zinc\collectors\physical.py
python .\commodity\zinc\src\zinc\collectors\lme.py
python .\shared\market_data\fx.py
python .\commodity\zinc\src\zinc\processing\build_physical_benchmark.py
python .\commodity\zinc\src\zinc\processing\build_intrinsic_bubbles.py
python .\commodity\zinc\src\zinc\processing\build_certificate_bubble.py
python .\commodity\zinc\src\zinc\processing\build_intrinsic_regression.py
```

The manual grade-analysis notebook is `notebooks/01_zinc_analysis.ipynb`; the presentation
notebook is `notebooks/02_bubble_analysis.ipynb`. Detailed methodology is in
[`docs/WORKFLOW.md`](docs/WORKFLOW.md), and the English report is in
[`reports/zinc/research`](../../reports/zinc/research/).

Both notebooks use interactive Plotly figures and were executed against this checkpoint.
The static research report retains its prior data vintage.
# Historical bubble distributions

`data/processed/bubble/zinc_bubble_distribution.csv` is the standardized Power BI table for all
computed zinc bubble types. Certificate-versus-physical rows include observed physical anchors
and bounded linear interpolations. `point_method` and `is_interpolated` identify every row. The table contains signed bubble percentages,
empirical `F(x)`, and `P(|Bubble| >= |x|)`. Distribution figures are written to
`data/processed/analysis`.
