# Copper Certificate Valuation

## Research question

Does the Iranian copper-cathode warehouse receipt trade at a premium or discount to a
comparable domestic physical-market price, after accounting for movements in LME cash copper
and the free-market USD/IRR exchange rate?

## Current checkpoint

- Data checkpoint: 2026-08-26
- Certificate: 266 calendar observations, 193 positive-trading days, through 2026-08-25
- Canonical physical market: 1,171 rows through 1405/06/02
- LME cash copper: 4,716 observations through 2026-08-25
- Free-market USD/IRR: 13,074 observations through 1405/05/31
- Processed physical benchmark and forward-gap diagnostic: `data/processed/physical`
- Bubble and regression outputs: `data/processed/bubble`
- Presentation timelines: `data/processed/analysis`

## Comparable physical underlying

The approved domestic benchmark includes only National Iranian Copper Industries Company
cathode under the historical symbols `NCI-CCAA-00` and `NCI-OACCAA-00`, using cash and
cash-matching contracts with positive executed price and quantity. Forward, credit, other
producers, and “copper cathode 2” are excluded from the comparable scope.

The daily physical price is volume weighted. The primary certificate valuation interpolates
the ratio of domestic physical price to LME–FX intrinsic price between exact physical/certificate
anchors. No extrapolation is allowed outside the observed anchor range. A time-series regression
using intrinsic price as its sole feature is retained as an experimental sensitivity check.

The separate `nci_copper_forward_gap.csv` diagnostic preserves the cash-only benchmark scope.
It covers 16 forward-trade dates and 26,420 tonnes strictly inside the 102-day cash gap,
comparing each forward weighted price with both cash anchors and a linear bridge.

## Main current result

The primary output contains 188 certificate-trading days from 2025-10-26 to 2026-08-24:
32 exact physical anchors and 156 interpolated days. The estimated certificate premium to
domestic physical value averages 5.64%, with a median of 7.17%. Interpretation is limited by
the small and temporally uneven physical anchor sample.

## Reproduction from the repository root

```powershell
python .\commodity\copper\src\copper\collectors\lme.py
python .\shared\market_data\fx.py
python .\commodity\copper\src\copper\collectors\certificate.py
python .\commodity\copper\src\copper\collectors\physical.py
python .\commodity\copper\src\copper\processing\build_physical_benchmark.py
python .\commodity\copper\src\copper\processing\build_intrinsic_bubbles.py
python .\commodity\copper\src\copper\processing\build_certificate_bubble.py
python .\commodity\copper\src\copper\processing\build_intrinsic_regression.py
python .\commodity\copper\src\copper\processing\build_presentation_timeline.py
python .\commodity\copper\src\copper\processing\build_forward_gap_analysis.py
```

The full methodology, source contracts, validations, and limitations are documented in
[`docs/WORKFLOW.md`](docs/WORKFLOW.md). The English research report is in
[`reports/copper/research`](../../reports/copper/research/).
