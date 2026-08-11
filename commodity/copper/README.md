# Copper Certificate Valuation

## Research question

Does the Iranian copper-cathode warehouse receipt trade at a premium or discount to a
comparable domestic physical-market price, after accounting for movements in LME cash copper
and the free-market USD/IRR exchange rate?

## Current checkpoint

- Data checkpoint: 2026-08-03
- Certificate: 246 calendar observations, 178 positive-trading days, through 2026-08-02
- Canonical physical market: 1,163 rows, including 1,154 positive trades, through 1405/05/04
- LME cash copper: 4,699 observations through 2026-07-31
- Free-market USD/IRR: 13,060 observations through 1405/05/11
- Processed layer: physical benchmark, two direct bubbles, primary certificate bubble,
  regression sensitivity output, and presentation timelines

## Comparable physical underlying

The approved domestic benchmark includes only National Iranian Copper Industries Company
cathode under the historical symbols `NCI-CCAA-00` and `NCI-OACCAA-00`, using cash and
cash-matching contracts with positive executed price and quantity. Forward, credit, other
producers, and “copper cathode 2” are excluded from the comparable scope.

The daily physical price is volume weighted. The primary certificate valuation interpolates
the ratio of domestic physical price to LME–FX intrinsic price between exact physical/certificate
anchors. No extrapolation is allowed outside the observed anchor range. A time-series regression
using intrinsic price as its sole feature is retained as an experimental sensitivity check.

## Main current result

The primary output contains 169 certificate-trading days from 2025-10-26 to 2026-07-26:
26 exact physical anchors and 143 interpolated days. The estimated certificate premium to
domestic physical value averages 5.17%, with a median of 6.13%. Interpretation is limited by
the small and temporally uneven physical anchor sample.

## Reproduction from the repository root

```powershell
python .\commodity\copper\src\copper\collectors\lme.py
python .\commodity\copper\src\copper\collectors\fx.py
python .\commodity\copper\src\copper\collectors\certificate.py
python .\commodity\copper\src\copper\collectors\physical.py
python .\commodity\copper\src\copper\processing\build_physical_benchmark.py
python .\commodity\copper\src\copper\processing\build_intrinsic_bubbles.py
python .\commodity\copper\src\copper\processing\build_certificate_bubble.py
python .\commodity\copper\src\copper\processing\build_intrinsic_regression.py
python .\commodity\copper\src\copper\processing\build_presentation_timeline.py
```

The full methodology, source contracts, validations, and limitations are documented in
[`docs/WORKFLOW.md`](docs/WORKFLOW.md). The English research report is in
[`reports/copper/research`](../../reports/copper/research/).
