# Zinc Certificate Valuation

## Research question

How does the Iranian zinc-ingot warehouse receipt trade relative to an eligible domestic
physical basket and to an LME–FX intrinsic benchmark?

## Current checkpoint

- Data checkpoint: 2026-08-15
- Certificate: 256 calendar observations, 184 positive-trading days, through 2026-08-13
- Broad physical raw data: 6,235 rows, including 3,462 positive trades, through 1405/05/18
- LME cash zinc: 4,709 observations from 2008-01-02 through 2026-08-14
- Free-market USD/IRR: 13,067 observations through 1405/05/20
- Official physical benchmark: 554 days from 2009-08-16 through 2026-08-09
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

The primary output contains 178 modeled certificate days from 2025-10-26 through 2026-08-09:
41 exact anchors and 137 interpolated days. The certificate premium to estimated domestic
physical value averages 0.34%, compared with an average direct certificate/intrinsic discount
of 20.13%. This difference demonstrates the economic importance of the domestic physical basis.

## Reproduction from the repository root

Canonical physical and certificate trades remain separate under `data/raw/{physical,certificate}`.
The physical benchmark is written to `data/processed/physical`; every bubble and regression table
is written to `data/processed/bubble`.

```powershell
python .\commodity\zinc\src\zinc\collectors\certificate.py
python .\commodity\zinc\src\zinc\collectors\physical.py
python .\commodity\zinc\src\zinc\collectors\lme.py
python .\commodity\zinc\src\zinc\collectors\fx.py
python .\commodity\zinc\src\zinc\processing\build_physical_benchmark.py
python .\commodity\zinc\src\zinc\processing\build_intrinsic_bubbles.py
python .\commodity\zinc\src\zinc\processing\build_certificate_bubble.py
python .\commodity\zinc\src\zinc\processing\build_intrinsic_regression.py
```

The manual grade-analysis notebook is `notebooks/01_zinc_analysis.ipynb`; the presentation
notebook is `notebooks/02_bubble_analysis.ipynb`. Detailed methodology is in
[`docs/WORKFLOW.md`](docs/WORKFLOW.md), and the English report is in
[`reports/zinc/research`](../../reports/zinc/research/).
